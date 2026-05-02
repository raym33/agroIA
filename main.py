import argparse
from pathlib import Path

from config import DEMO_IRRIGATION_CSV, DEMO_PEST_RISK_CSV
from modules.data_sources import download_url_to_file, fetch_aemet_api_resource
from modules.demo_data import generate_demo_datasets
from modules.drone_vision import detect_pests_in_image
from modules.irrigation import predict_irrigation, train_irrigation_model
from modules.model_benchmark import benchmark_irrigation_models, benchmark_pest_models
from modules.pest_risk import predict_pest_risk, train_pest_risk_model
from modules.preprocess import prepare_siam_daily_csv
from modules.traceability import init_db, list_recent_decisions, log_decision
from modules.io_utils import ensure_project_dirs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Local-first precision agriculture MVP: irrigation, pests, and traceability."
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "init-demo-data",
        help="Generate demo datasets to test the flow without real data.",
    )
    subparsers.add_parser(
        "train-all",
        help="Train both irrigation and pest models using the configured CSV files.",
    )

    train_irrigation_parser = subparsers.add_parser(
        "train-irrigation", help="Train only the irrigation model."
    )
    train_irrigation_parser.add_argument(
        "--csv",
        default=str(DEMO_IRRIGATION_CSV),
        help="Path to the irrigation CSV.",
    )

    train_pests_parser = subparsers.add_parser(
        "train-pests", help="Train only the pest risk model."
    )
    train_pests_parser.add_argument(
        "--csv",
        default=str(DEMO_PEST_RISK_CSV),
        help="Path to the pest CSV.",
    )

    benchmark_parser = subparsers.add_parser(
        "benchmark-models",
        help="Compare RandomForest, CatBoost, and XGBoost on your datasets.",
    )
    benchmark_parser.add_argument(
        "--task",
        choices=["all", "irrigation", "pests"],
        default="all",
        help="Which benchmark to run.",
    )
    benchmark_parser.add_argument(
        "--irrigation-csv",
        default=str(DEMO_IRRIGATION_CSV),
        help="Path to the irrigation CSV.",
    )
    benchmark_parser.add_argument(
        "--pests-csv",
        default=str(DEMO_PEST_RISK_CSV),
        help="Path to the pest CSV.",
    )

    predict_parser = subparsers.add_parser(
        "predict",
        help="Calculate irrigation recommendation and pest risk for one plot.",
    )
    predict_parser.add_argument("--parcel-id", default="PLOT-001")
    predict_parser.add_argument("--crop-type", default="vegetables")
    predict_parser.add_argument("--temp-c", required=True, type=float)
    predict_parser.add_argument("--humidity-pct", required=True, type=float)
    predict_parser.add_argument("--et0-mm", required=True, type=float)
    predict_parser.add_argument("--soil-moisture-pct", required=True, type=float)
    predict_parser.add_argument("--rain-mm", required=True, type=float)
    predict_parser.add_argument("--ndvi", required=True, type=float)
    predict_parser.add_argument("--days-since-rain", required=True, type=int)
    predict_parser.add_argument("--notes", default="")
    predict_parser.add_argument(
        "--save",
        action="store_true",
        help="Save the recommendation into SQLite.",
    )

    detect_parser = subparsers.add_parser(
        "detect-pests-image",
        help="Run visual detection if a local YOLO model is available.",
    )
    detect_parser.add_argument("--image", required=True, help="Path to the image.")
    detect_parser.add_argument("--confidence", default=0.5, type=float)

    download_parser = subparsers.add_parser(
        "download-url",
        help="Download a CSV or JSON file from a direct URL into data/raw.",
    )
    download_parser.add_argument("--url", required=True)
    download_parser.add_argument("--output-name", required=True)

    aemet_parser = subparsers.add_parser(
        "fetch-aemet-resource",
        help="Download an AEMET OpenData resource using the API flow.",
    )
    aemet_parser.add_argument("--api-key", required=True)
    aemet_parser.add_argument(
        "--resource-path",
        required=True,
        help="Path under /opendata/api/, for example valores/climatologicos/inventarioestaciones/todasestaciones/.",
    )
    aemet_parser.add_argument("--output-name", required=True)

    siam_parser = subparsers.add_parser(
        "prepare-siam",
        help="Convert a daily SIAM CSV into base irrigation and pest tables.",
    )
    siam_parser.add_argument("--input-csv", required=True)
    siam_parser.add_argument("--crop-type", required=True)
    siam_parser.add_argument(
        "--soil-moisture-pct",
        type=float,
        default=22.0,
        help="Fallback soil moisture value if no soil probe exists yet.",
    )
    siam_parser.add_argument(
        "--output-prefix",
        required=True,
        help="Prefix for the prepared CSV files in data/processed.",
    )

    subparsers.add_parser(
        "recent-decisions",
        help="List the most recent decisions stored in traceability.",
    )

    return parser


def run_predict_command(args: argparse.Namespace) -> None:
    water_l_m2 = predict_irrigation(
        temp_c=args.temp_c,
        humidity_pct=args.humidity_pct,
        et0_mm=args.et0_mm,
        soil_moisture_pct=args.soil_moisture_pct,
        rain_mm=args.rain_mm,
        crop_type=args.crop_type,
    )
    pest_risk = predict_pest_risk(
        temp_c=args.temp_c,
        humidity_pct=args.humidity_pct,
        et0_mm=args.et0_mm,
        ndvi=args.ndvi,
        days_since_rain=args.days_since_rain,
        crop_type=args.crop_type,
    )

    print(f"Plot: {args.parcel_id}")
    print(f"Recommended water: {water_l_m2:.2f} L/m2")
    print(f"Pest risk: {pest_risk}")

    if args.save:
        log_decision(
            parcel_id=args.parcel_id,
            crop_type=args.crop_type,
            water_recommended_l_m2=water_l_m2,
            pest_risk=pest_risk,
            notes=args.notes,
            data_source="manual/local-model",
        )
        print("Decision saved to traceability.")


def main() -> None:
    ensure_project_dirs()
    init_db()

    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    if args.command == "init-demo-data":
        generate_demo_datasets()
        print("Demo datasets generated.")
        return

    if args.command == "train-all":
        irrigation_metrics = train_irrigation_model(DEMO_IRRIGATION_CSV)
        pest_metrics = train_pest_risk_model(DEMO_PEST_RISK_CSV)
        print(f"Irrigation model trained. MAE={irrigation_metrics['mae']:.3f}, R2={irrigation_metrics['r2']:.3f}")
        print(
            "Pest model trained. "
            f"accuracy={pest_metrics['accuracy']:.3f}, macro_f1={pest_metrics['macro_f1']:.3f}"
        )
        return

    if args.command == "train-irrigation":
        irrigation_metrics = train_irrigation_model(Path(args.csv))
        print(f"Irrigation model trained. MAE={irrigation_metrics['mae']:.3f}, R2={irrigation_metrics['r2']:.3f}")
        return

    if args.command == "train-pests":
        pest_metrics = train_pest_risk_model(Path(args.csv))
        print(
            "Pest model trained. "
            f"accuracy={pest_metrics['accuracy']:.3f}, macro_f1={pest_metrics['macro_f1']:.3f}"
        )
        return

    if args.command == "benchmark-models":
        if args.task in {"all", "irrigation"}:
            irrigation_results = benchmark_irrigation_models(Path(args.irrigation_csv))
            print(f"Irrigation benchmark saved to {irrigation_results['output_path']}")
            for row in irrigation_results["rows"]:
                print(row)
        if args.task in {"all", "pests"}:
            pest_results = benchmark_pest_models(Path(args.pests_csv))
            print(f"Pest benchmark saved to {pest_results['output_path']}")
            for row in pest_results["rows"]:
                print(row)
        return

    if args.command == "predict":
        run_predict_command(args)
        return

    if args.command == "detect-pests-image":
        detections = detect_pests_in_image(Path(args.image), confidence=args.confidence)
        print(f"Detections: {detections}")
        return

    if args.command == "download-url":
        output_path = download_url_to_file(args.url, args.output_name)
        print(f"Downloaded to {output_path}")
        return

    if args.command == "fetch-aemet-resource":
        output_path = fetch_aemet_api_resource(
            api_key=args.api_key,
            resource_path=args.resource_path,
            output_name=args.output_name,
        )
        print(f"AEMET resource saved to {output_path}")
        return

    if args.command == "prepare-siam":
        outputs = prepare_siam_daily_csv(
            input_csv=Path(args.input_csv),
            crop_type=args.crop_type,
            soil_moisture_pct=args.soil_moisture_pct,
            output_prefix=args.output_prefix,
        )
        print(f"Irrigation base prepared at {outputs['irrigation']}")
        print(f"Pest base prepared at {outputs['pest']}")
        return

    if args.command == "recent-decisions":
        for decision in list_recent_decisions(limit=10):
            print(decision)
        return


if __name__ == "__main__":
    main()

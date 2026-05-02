from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from config import (
    BASE_DIR,
    DEMO_IRRIGATION_CSV,
    DEMO_PEST_RISK_CSV,
    IMAGE_UPLOADS_DIR,
    IRRIGATION_MODEL_PATH,
    LOCAL_LLM_BASE_URL,
    LOCAL_LLM_MODEL,
    PEST_RISK_MODEL_PATH,
    RAW_DATA_DIR,
    TABLE_UPLOADS_DIR,
    YOLO_MODEL_PATH,
)
from modules.decision_support import build_action_plan
from modules.demo_data import generate_demo_datasets
from modules.drone_vision import detect_pests_in_image
from modules.io_utils import ensure_project_dirs
from modules.irrigation import (
    IRRIGATION_FEATURES,
    IRRIGATION_TARGET,
    predict_irrigation,
    train_irrigation_model,
)
from modules.llm_advisor import (
    generate_daily_advice,
    generate_visual_advice,
    get_local_llm_status,
)
from modules.pest_risk import (
    PEST_FEATURES,
    PEST_TARGET,
    predict_pest_risk,
    train_pest_risk_model,
)
from modules.preprocess import prepare_siam_daily_csv
from modules.traceability import init_db, list_recent_decisions, log_decision


st.set_page_config(
    page_title="AgroIA",
    page_icon="🌿",
    layout="wide",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
          --soil: #4f3728;
          --leaf: #2f6f47;
          --leaf-soft: #7ea46b;
          --sand: #efe6d1;
          --mist: #fbf7ee;
          --ink: #2d2b26;
          --muted: #6f685c;
          --alert: #a54b2a;
        }
        .stApp {
          color: var(--ink);
          background:
            radial-gradient(circle at top left, rgba(126,164,107,0.16), transparent 28%),
            radial-gradient(circle at top right, rgba(90,61,43,0.10), transparent 22%),
            linear-gradient(180deg, #fcfaf4 0%, #f3eee1 100%);
        }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
        .stApp p, .stApp label, .stApp span, .stApp div, .stApp small {
          color: var(--ink);
        }
        .hero {
          background: linear-gradient(135deg, rgba(47,111,71,0.96), rgba(90,61,43,0.93));
          color: white !important;
          padding: 1.45rem 1.55rem;
          border-radius: 20px;
          margin-bottom: 1rem;
          box-shadow: 0 18px 40px rgba(58, 51, 42, 0.16);
        }
        .hero h1, .hero p {
          color: white !important;
        }
        .hero h1 {
          margin: 0;
          font-size: 2rem;
          line-height: 1.05;
        }
        .hero p {
          margin: 0.6rem 0 0 0;
          max-width: 900px;
          color: rgba(255,255,255,0.9) !important;
        }
        .metric-card {
          background: rgba(255,255,255,0.88);
          border: 1px solid rgba(47,111,71,0.12);
          border-radius: 16px;
          padding: 1rem 1.1rem;
          box-shadow: 0 10px 24px rgba(78, 69, 55, 0.07);
        }
        .metric-label {
          font-size: 0.82rem;
          color: #5d5a55 !important;
          margin-bottom: 0.3rem;
          text-transform: uppercase;
          letter-spacing: 0.03em;
        }
        .metric-value {
          font-size: 2rem;
          font-weight: 700;
          color: var(--soil) !important;
          line-height: 1.05;
        }
        .metric-note {
          margin-top: 0.35rem;
          color: #45634a !important;
          font-size: 0.92rem;
        }
        .box-soft {
          background: rgba(255,255,255,0.76);
          border-radius: 16px;
          padding: 1rem 1.1rem;
          border: 1px solid rgba(90,61,43,0.1);
        }
        .callout {
          background: rgba(255,255,255,0.84);
          border-left: 4px solid #2f6f47;
          border-radius: 14px;
          padding: 0.95rem 1rem;
          margin: 0.6rem 0 1rem 0;
        }
        .callout strong, .callout p {
          color: var(--ink) !important;
        }
        .algo-chip {
          display: inline-block;
          margin: 0.15rem 0.35rem 0.15rem 0;
          padding: 0.35rem 0.65rem;
          border-radius: 999px;
          background: rgba(47,111,71,0.1);
          color: #28573a !important;
          border: 1px solid rgba(47,111,71,0.15);
          font-size: 0.9rem;
        }
        .stTabs [data-baseweb="tab-list"] {
          gap: 0.7rem;
        }
        .stTabs [data-baseweb="tab"] {
          background: rgba(255,255,255,0.52);
          border-radius: 999px;
          padding: 0.4rem 0.9rem;
        }
        .stTabs [aria-selected="true"] {
          background: rgba(47,111,71,0.12);
        }
        .stTabs [data-baseweb="tab"] p {
          color: var(--soil) !important;
          font-weight: 600;
        }
        .stFileUploader label, .stCheckbox label,
        .stTextInput label, .stTextArea label, .stNumberInput label,
        .stSelectbox label, .stMultiSelect label {
          color: var(--ink) !important;
          font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def model_ready() -> bool:
    return IRRIGATION_MODEL_PATH.exists() and PEST_RISK_MODEL_PATH.exists()


def render_metric_card(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_callout(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="callout">
          <strong>{title}</strong>
          <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def bootstrap_demo_models() -> None:
    generate_demo_datasets()
    irrigation_metrics = train_irrigation_model(DEMO_IRRIGATION_CSV)
    pest_metrics = train_pest_risk_model(DEMO_PEST_RISK_CSV)
    st.success(
        "Demo models trained. "
        f"Irrigation MAE={irrigation_metrics['mae']:.3f}, R2={irrigation_metrics['r2']:.3f}. "
        f"Pests accuracy={pest_metrics['accuracy']:.3f}, macro F1={pest_metrics['macro_f1']:.3f}."
    )


def save_uploaded_file(uploaded_file, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / uploaded_file.name
    destination.write_bytes(uploaded_file.getbuffer())
    return destination


def load_uploaded_table(uploaded_file, sheet_name: str | None = None) -> pd.DataFrame:
    raw_bytes = uploaded_file.getvalue()
    suffix = Path(uploaded_file.name).suffix.lower()
    buffer = BytesIO(raw_bytes)

    if suffix == ".csv":
        return pd.read_csv(buffer)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(buffer, sheet_name=sheet_name)
    raise ValueError("Unsupported format. Use CSV or XLSX.")


def list_excel_sheets(uploaded_file) -> list[str]:
    raw_bytes = uploaded_file.getvalue()
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix not in {".xlsx", ".xls"}:
        return []
    workbook = pd.ExcelFile(BytesIO(raw_bytes))
    return list(workbook.sheet_names)


def get_missing_columns(df: pd.DataFrame, required_columns: list[str]) -> list[str]:
    return [column for column in required_columns if column not in df.columns]


def render_algorithm_explainer() -> None:
    with st.expander("Which algorithm the app uses today", expanded=True):
        st.markdown(
            """
            <span class="algo-chip">RandomForestRegressor</span>
            <span class="algo-chip">RandomForestClassifier</span>
            <span class="algo-chip">Optional YOLO</span>
            <span class="algo-chip">Gemma 4 26B as copilot only</span>
            """,
            unsafe_allow_html=True,
        )
        st.write(
            "Irrigation is not computed by an LLM. It comes from a `RandomForestRegressor` trained on "
            "`temperature`, `humidity`, `ET0`, `soil moisture`, `rainfall`, and `crop type`."
        )
        st.write(
            "Pest risk comes from a `RandomForestClassifier` using "
            "`temperature`, `humidity`, `ET0`, `NDVI`, `days since rain`, and `crop type`."
        )
        st.write(
            "Gemma 4 26B is not deciding irrigation liters or risk classes: today it only summarizes, explains, and, if the multimodal endpoint responds, comments on images."
        )
        st.write(
            "I use `RandomForest` because for a tabular MVP with a few hundred or a few thousand rows it is usually robust, non-linear, and fast to recalibrate locally."
        )


def render_sidebar() -> tuple[bool, str, str]:
    st.sidebar.header("Local control")
    st.sidebar.write(
        "Numeric prediction runs on tabular models. Gemma is used as an explanation and visual support layer."
    )

    status_text = "ready" if model_ready() else "models missing"
    st.sidebar.caption(f"Tabular model status: {status_text}")

    if st.sidebar.button("Generate demo + train models", use_container_width=True):
        bootstrap_demo_models()

    use_local_llm = st.sidebar.toggle("Enable local Gemma", value=True)
    llm_base_url = st.sidebar.text_input("Local endpoint", value=LOCAL_LLM_BASE_URL)
    llm_model = st.sidebar.text_input("Local model", value=LOCAL_LLM_MODEL)
    st.sidebar.caption("Gemma 26B is higher quality, but it can be noticeably slower in a local setup.")

    llm_status = get_local_llm_status(base_url=llm_base_url)
    if llm_status["ok"]:
        st.sidebar.success("Local LLM available")
        st.sidebar.caption(", ".join(llm_status["models"][:3]))
    else:
        st.sidebar.warning("Local LLM unavailable")
        st.sidebar.caption(llm_status["error"])

    return use_local_llm, llm_base_url, llm_model


def render_prediction_tab(use_local_llm: bool, llm_base_url: str, llm_model: str) -> None:
    st.subheader("Daily prediction by plot")
    render_callout(
        "Recommended flow",
        "First calculate the numeric recommendation. Upload images in the Photos tab. Historical Excel and CSV files belong in the Historical spreadsheets tab.",
    )
    render_algorithm_explainer()

    if not model_ready():
        st.info("No trained models are available yet. Use the side button to generate and train demo data.")
        return

    with st.form("predict-form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            parcel_id = st.text_input("Plot", value="PLOT-001")
            crop_type = st.selectbox("Crop", options=["vegetables", "citrus", "orchard"])
            temp_c = st.number_input("Temperature (C)", value=28.0, step=0.1)
            humidity_pct = st.number_input("Relative humidity (%)", value=47.0, step=0.1)
        with col2:
            et0_mm = st.number_input("ET0 (mm)", value=5.9, step=0.1)
            soil_moisture_pct = st.number_input("Soil moisture (%)", value=21.0, step=0.1)
            rain_mm = st.number_input("Rainfall (mm)", value=0.0, step=0.1)
            ndvi = st.number_input("NDVI", value=0.72, step=0.01, min_value=0.0, max_value=1.0)
        with col3:
            days_since_rain = st.number_input("Days since rain", value=11, step=1, min_value=0)
            notes = st.text_area("Field notes", value="", height=120)
            save_decision = st.checkbox("Save in traceability", value=True)

        submitted = st.form_submit_button("Calculate recommendation", use_container_width=True)

    if submitted:
        water_l_m2 = predict_irrigation(
            temp_c=float(temp_c),
            humidity_pct=float(humidity_pct),
            et0_mm=float(et0_mm),
            soil_moisture_pct=float(soil_moisture_pct),
            rain_mm=float(rain_mm),
            crop_type=crop_type,
        )
        pest_risk = predict_pest_risk(
            temp_c=float(temp_c),
            humidity_pct=float(humidity_pct),
            et0_mm=float(et0_mm),
            ndvi=float(ndvi),
            days_since_rain=int(days_since_rain),
            crop_type=crop_type,
        )

        latest_prediction = {
            "parcel_id": parcel_id,
            "crop_type": crop_type,
            "temp_c": float(temp_c),
            "humidity_pct": float(humidity_pct),
            "et0_mm": float(et0_mm),
            "soil_moisture_pct": float(soil_moisture_pct),
            "rain_mm": float(rain_mm),
            "ndvi": float(ndvi),
            "days_since_rain": int(days_since_rain),
            "notes": notes,
            "water_l_m2": water_l_m2,
            "pest_risk": pest_risk,
        }
        st.session_state["latest_prediction"] = latest_prediction
        st.session_state.pop("latest_llm_advice", None)

        if save_decision:
            log_decision(
                parcel_id=parcel_id,
                crop_type=crop_type,
                water_recommended_l_m2=water_l_m2,
                pest_risk=pest_risk,
                notes=notes,
                data_source="streamlit/local-model",
            )

    latest = st.session_state.get("latest_prediction")
    if not latest:
        return

    actions = build_action_plan(
        water_l_m2=float(latest["water_l_m2"]),
        pest_risk=str(latest["pest_risk"]),
        crop_type=str(latest["crop_type"]),
        soil_moisture_pct=float(latest["soil_moisture_pct"]),
        rain_mm=float(latest["rain_mm"]),
    )

    m1, m2, m3 = st.columns(3)
    with m1:
        render_metric_card("Recommended water", f"{float(latest['water_l_m2']):.2f} L/m2", "Local per-plot estimate")
    with m2:
        render_metric_card("Pest risk", str(latest["pest_risk"]), "Local tabular classification")
    with m3:
        priority = (
            "High"
            if str(latest["pest_risk"]) == "HIGH" or float(latest["water_l_m2"]) >= 4.5
            else "Medium"
            if str(latest["pest_risk"]) == "MEDIUM"
            else "Normal"
        )
        render_metric_card("Operational priority", priority, "Suggested order for today")

    st.markdown("### Suggested actions")
    st.markdown('<div class="box-soft">', unsafe_allow_html=True)
    for action in actions:
        st.write(f"- {action}")
    st.markdown("</div>", unsafe_allow_html=True)

    if use_local_llm:
        st.caption("Gemma 26B is used here as an explainer. It does not change the numeric prediction.")
        if st.button("Generate local Gemma summary", use_container_width=True):
            with st.spinner("Querying local Gemma..."):
                try:
                    advice = generate_daily_advice(
                        parcel_id=str(latest["parcel_id"]),
                        crop_type=str(latest["crop_type"]),
                        water_l_m2=float(latest["water_l_m2"]),
                        pest_risk=str(latest["pest_risk"]),
                        temp_c=float(latest["temp_c"]),
                        humidity_pct=float(latest["humidity_pct"]),
                        et0_mm=float(latest["et0_mm"]),
                        soil_moisture_pct=float(latest["soil_moisture_pct"]),
                        rain_mm=float(latest["rain_mm"]),
                        ndvi=float(latest["ndvi"]),
                        days_since_rain=int(latest["days_since_rain"]),
                        base_url=llm_base_url,
                        model=llm_model,
                    )
                    st.session_state["latest_llm_advice"] = advice
                except Exception as exc:
                    st.warning(f"Could not generate the local summary: {exc}")

        if st.session_state.get("latest_llm_advice"):
            st.markdown("### Local AI reading")
            st.markdown(
                f'<div class="box-soft">{st.session_state["latest_llm_advice"]}</div>',
                unsafe_allow_html=True,
            )


def render_visual_tab(use_local_llm: bool, llm_base_url: str, llm_model: str) -> None:
    st.subheader("Planting or harvest photos")
    render_callout(
        "Upload photos here",
        "This area is for crop, leaf, fruit, whole-plot, harvest, or drone images. The current numeric prediction does not use the image automatically; the image is for local visual inspection.",
    )

    upload_col, result_col = st.columns([1.15, 1])

    with upload_col:
        image_file = st.file_uploader(
            "Upload a crop image",
            type=["png", "jpg", "jpeg", "webp"],
            key="photo-upload",
        )
        crop_type = st.selectbox(
            "Crop in the image",
            options=["vegetables", "citrus", "orchard"],
            key="photo-crop-type",
        )
        image_context = st.selectbox(
            "What the image shows",
            options=["whole plot", "leaf", "fruit", "harvest", "drone"],
            key="photo-context",
        )
        yolo_confidence = st.slider("Minimum YOLO confidence", min_value=0.10, max_value=0.95, value=0.50, step=0.05)

        if image_file:
            st.image(image_file, caption=image_file.name, use_container_width=True)
            saved_image_path = save_uploaded_file(image_file, IMAGE_UPLOADS_DIR)
            st.session_state["latest_image_path"] = str(saved_image_path)
            st.caption(f"Image saved to {saved_image_path}")

    with result_col:
        if not st.session_state.get("latest_image_path"):
            st.info("Upload an image to enable visual analysis.")
            return

        saved_image = Path(st.session_state["latest_image_path"])
        if YOLO_MODEL_PATH.exists():
            if st.button("Analyze with local visual detector", use_container_width=True):
                try:
                    detections = detect_pests_in_image(saved_image, confidence=float(yolo_confidence))
                    st.session_state["latest_yolo_detections"] = detections
                except Exception as exc:
                    st.warning(f"Could not run YOLO: {exc}")
        else:
            st.warning("`models/pest_detector.pt` is not available yet. You can already upload photos, but the YOLO detector is not connected yet.")

        if st.session_state.get("latest_yolo_detections") is not None:
            detections = st.session_state["latest_yolo_detections"]
            if detections:
                st.markdown("### Visual detections")
                st.dataframe(pd.DataFrame(detections), use_container_width=True)
            else:
                st.info("The detector returned no objects above the configured threshold.")

        if use_local_llm:
            st.caption("Gemma 26B has vision, but the result depends on whether the local endpoint supports multimodal input.")
            if st.button("Describe image with Gemma Vision", use_container_width=True):
                with st.spinner("Querying local Gemma Vision..."):
                    try:
                        visual_advice = generate_visual_advice(
                            image_path=saved_image,
                            crop_type=crop_type,
                            image_context=image_context,
                            base_url=llm_base_url,
                            model=llm_model,
                        )
                        st.session_state["latest_visual_advice"] = visual_advice
                    except Exception as exc:
                        st.warning(f"Could not analyze the image with Gemma: {exc}")

            if st.session_state.get("latest_visual_advice"):
                st.markdown("### Local visual AI reading")
                st.markdown(
                    f'<div class="box-soft">{st.session_state["latest_visual_advice"]}</div>',
                    unsafe_allow_html=True,
                )


def render_history_files_tab() -> None:
    st.subheader("Historical Excel and CSV files")
    render_callout(
        "Upload historical files here",
        "This area is for Excel or CSV files with past harvests, irrigation, pests, production, and field visits. If the schema matches, you can retrain from here.",
    )

    template_path = BASE_DIR / "templates" / "farmer_data_template_mvp.xlsx"
    questionnaire_path = BASE_DIR / "docs" / "farmer_discovery_questionnaire.md"
    download_col1, download_col2 = st.columns(2)
    with download_col1:
        if template_path.exists():
            st.download_button(
                "Download Excel template",
                data=template_path.read_bytes(),
                file_name=template_path.name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
    with download_col2:
        if questionnaire_path.exists():
            st.download_button(
                "Download questionnaire",
                data=questionnaire_path.read_text(encoding="utf-8"),
                file_name=questionnaire_path.name,
                mime="text/markdown",
                use_container_width=True,
            )

    top_left, top_right = st.columns([1.2, 1])

    with top_left:
        selected_sheet = None
        historical_file = st.file_uploader(
            "Upload a historical Excel or CSV file",
            type=["csv", "xlsx", "xls"],
            key="historical-file",
        )

        if historical_file:
            suffix = Path(historical_file.name).suffix.lower()
            selected_sheet = None
            if suffix in {".xlsx", ".xls"}:
                sheets = list_excel_sheets(historical_file)
                selected_sheet = st.selectbox("Excel sheet", options=sheets, key="historical-sheet")

            try:
                preview_df = load_uploaded_table(historical_file, sheet_name=selected_sheet).head(50)
                st.dataframe(preview_df, use_container_width=True)
                st.caption(f"Detected columns: {', '.join(preview_df.columns.astype(str).tolist())}")
                st.session_state["historical_preview_df"] = preview_df
            except Exception as exc:
                st.error(f"Could not read the file: {exc}")
                st.session_state.pop("historical_preview_df", None)

    with top_right:
        st.markdown("#### What kind of file is this")
        file_role = st.selectbox(
            "Intended use",
            options=[
                "mixed_history",
                "irrigation_labeled",
                "pest_labeled",
            ],
            format_func=lambda value: {
                "mixed_history": "Mixed historical file",
                "irrigation_labeled": "Labeled irrigation dataset",
                "pest_labeled": "Labeled pest dataset",
            }[value],
        )

        if historical_file:
            saved_path = save_uploaded_file(historical_file, TABLE_UPLOADS_DIR)
            st.caption(f"File saved to {saved_path}")
            df = load_uploaded_table(historical_file, sheet_name=selected_sheet)

            if file_role == "irrigation_labeled":
                required = IRRIGATION_FEATURES + [IRRIGATION_TARGET]
                missing = get_missing_columns(df, required)
                if missing:
                    st.error(f"Missing columns to train irrigation: {', '.join(missing)}")
                elif st.button("Train irrigation model with this file", use_container_width=True):
                    training_path = TABLE_UPLOADS_DIR / f"{saved_path.stem}_irrigation_training.csv"
                    df.to_csv(training_path, index=False)
                    metrics = train_irrigation_model(training_path)
                    st.success(f"Irrigation model retrained. MAE={metrics['mae']:.3f}, R2={metrics['r2']:.3f}")

            elif file_role == "pest_labeled":
                required = PEST_FEATURES + [PEST_TARGET]
                missing = get_missing_columns(df, required)
                if missing:
                    st.error(f"Missing columns to train pests: {', '.join(missing)}")
                elif st.button("Train pest model with this file", use_container_width=True):
                    training_path = TABLE_UPLOADS_DIR / f"{saved_path.stem}_pest_training.csv"
                    df.to_csv(training_path, index=False)
                    metrics = train_pest_risk_model(training_path)
                    st.success(
                        f"Pest model retrained. accuracy={metrics['accuracy']:.3f}, macro F1={metrics['macro_f1']:.3f}"
                    )
            else:
                st.info("The file is stored as mixed history. You can clean or split it later and then use it for training.")

    st.markdown("### Prepare daily SIAM CSV")
    siam_left, siam_right = st.columns(2)
    with siam_left:
        uploaded_siam = st.file_uploader(
            "Upload a daily SIAM CSV",
            type=["csv"],
            key="siam-uploader",
        )
        siam_crop_type = st.selectbox(
            "Crop for SIAM data",
            options=["vegetables", "citrus", "orchard"],
            key="siam-crop",
        )
    with siam_right:
        siam_soil_moisture = st.number_input(
            "Fallback soil moisture (%)",
            value=22.0,
            step=0.1,
            key="siam-soil",
        )
        siam_prefix = st.text_input("Output prefix", value="siam_local")

    if st.button("Prepare base tables from SIAM", use_container_width=True):
        if not uploaded_siam:
            st.error("Upload a SIAM CSV first.")
        else:
            raw_path = RAW_DATA_DIR / uploaded_siam.name
            raw_path.write_bytes(uploaded_siam.getbuffer())
            outputs = prepare_siam_daily_csv(
                input_csv=raw_path,
                crop_type=siam_crop_type,
                soil_moisture_pct=float(siam_soil_moisture),
                output_prefix=siam_prefix,
            )
            st.success("SIAM CSV prepared.")
            st.write(outputs["irrigation"])
            st.write(outputs["pest"])
            preview_df = pd.read_csv(outputs["irrigation"]).head(20)
            st.dataframe(preview_df, use_container_width=True)


def render_history_tab() -> None:
    st.subheader("Decision history")
    rows = list_recent_decisions(limit=50)
    if not rows:
        st.info("No decisions have been recorded yet.")
        return

    history_df = pd.DataFrame(rows)
    st.dataframe(history_df, use_container_width=True)

    if len(history_df) < 2:
        st.caption("The chart appears once at least two decisions have been recorded.")
        return

    chart_df = history_df.copy()
    chart_df["created_at"] = pd.to_datetime(chart_df["created_at"], utc=True, errors="coerce")
    chart_df = chart_df.dropna(subset=["created_at", "water_recommended_l_m2"])
    if len(chart_df) < 2:
        st.caption("There are still not enough valid points for the chart.")
        return

    chart_df = chart_df.sort_values("created_at")
    chart_df = chart_df.set_index("created_at")
    st.line_chart(chart_df[["water_recommended_l_m2"]], height=240)


def main() -> None:
    ensure_project_dirs()
    init_db()
    inject_styles()

    st.markdown(
        """
        <div class="hero">
          <h1>AgroIA</h1>
          <p>
            Optimized irrigation, pest risk, field images, and historical files in one local-first app.
            Irrigation liters and risk classes come from dedicated models; Gemma remains a visual and explanatory copilot.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    use_local_llm, llm_base_url, llm_model = render_sidebar()
    tab1, tab2, tab3, tab4 = st.tabs(["Prediction", "Photos", "Historical spreadsheets", "History"])
    with tab1:
        render_prediction_tab(use_local_llm, llm_base_url, llm_model)
    with tab2:
        render_visual_tab(use_local_llm, llm_base_url, llm_model)
    with tab3:
        render_history_files_tab()
    with tab4:
        render_history_tab()


if __name__ == "__main__":
    main()

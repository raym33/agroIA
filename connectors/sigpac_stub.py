from dataclasses import dataclass


@dataclass
class SigpacReference:
    province_code: str
    municipality_code: str
    polygon_code: str
    parcel_code: str
    recinto_code: str | None = None

    def human_key(self) -> str:
        recinto = self.recinto_code or "ALL"
        return (
            f"{self.province_code}-"
            f"{self.municipality_code}-"
            f"{self.polygon_code}-"
            f"{self.parcel_code}-"
            f"{recinto}"
        )


def build_sigpac_filter(reference: SigpacReference) -> dict[str, str]:
    payload = {
        "province_code": reference.province_code,
        "municipality_code": reference.municipality_code,
        "polygon_code": reference.polygon_code,
        "parcel_code": reference.parcel_code,
    }
    if reference.recinto_code:
        payload["recinto_code"] = reference.recinto_code
    return payload

"""schemas untuk member Hit ke API Kita."""

from pydantic import AnyHttpUrl, BaseModel, Field, SecretStr

# TODO : Balik kesni ya , ini terlalu minimalis


class MemberInDB(BaseModel):
    member_id: str = Field(..., description="ID unik untuk member")
    pin: SecretStr = Field(..., description="PIN untuk member")
    password: SecretStr = Field(..., description="Password untuk member")
    is_active: bool = Field(default=True, description="Status keaktifan member")
    ip_address: str = Field(..., description="Alamat IP member")
    report_url: AnyHttpUrl = Field(..., description="URL untuk laporan member")
    allow_nosign: bool = Field(
        default=False,
        description="Apakah member diizinkan untuk hit tanpa Signature(ini Biasanya Otomax Signature)",
    )

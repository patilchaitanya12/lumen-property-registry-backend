from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class OwnerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)

    record_id: str | None = None
    normalized_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    title: str | None = None

    owner_type: str | None = None
    vip_tier: str | None = None
    gender: str | None = None
    gender_source: str | None = None

    source_community: str | None = None
    source_file: str | None = None

    country: str | None = None
    id_number: str | None = None
    uae_id_number: str | None = None
    unified_number: str | None = None
    passport_expiry_date: date | None = None
    birth_date: date | None = None

    property_count: int | None = Field(default=None, ge=0)
    communities_owned: int | None = Field(default=None, ge=0)
    community_list: str | None = None
    buildings_list: str | None = None

    is_multi_property: bool | None = None
    is_portfolio_investor: bool | None = None
    has_cross_community: bool | None = None
    portfolio_tier: str | None = None
    has_plot: bool | None = None
    has_apartment: bool | None = None
    has_villa: bool | None = None
    is_reachable: bool | None = None

    is_active: bool = True
    notes: str | None = None


class OwnerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)

    record_id: str | None = None
    normalized_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    title: str | None = None

    owner_type: str | None = None
    vip_tier: str | None = None
    gender: str | None = None
    gender_source: str | None = None

    source_community: str | None = None
    source_file: str | None = None

    country: str | None = None
    id_number: str | None = None
    uae_id_number: str | None = None
    unified_number: str | None = None
    passport_expiry_date: date | None = None
    birth_date: date | None = None

    property_count: int | None = Field(default=None, ge=0)
    communities_owned: int | None = Field(default=None, ge=0)
    community_list: str | None = None
    buildings_list: str | None = None

    is_multi_property: bool | None = None
    is_portfolio_investor: bool | None = None
    has_cross_community: bool | None = None
    portfolio_tier: str | None = None
    has_plot: bool | None = None
    has_apartment: bool | None = None
    has_villa: bool | None = None
    is_reachable: bool | None = None

    is_active: bool | None = None
    notes: str | None = None


class OwnerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    owner_id: str
    record_id: str | None
    name: str
    normalized_name: str | None

    first_name: str | None
    last_name: str | None
    title: str | None

    owner_type: str | None
    vip_tier: str | None
    gender: str | None
    gender_source: str | None

    source_community: str | None
    source_file: str | None

    country: str | None
    id_number: str | None
    uae_id_number: str | None
    unified_number: str | None
    passport_expiry_date: date | None
    birth_date: date | None

    property_count: int | None
    communities_owned: int | None
    community_list: str | None
    buildings_list: str | None

    is_multi_property: bool | None
    is_portfolio_investor: bool | None
    has_cross_community: bool | None
    portfolio_tier: str | None
    has_plot: bool | None
    has_apartment: bool | None
    has_villa: bool | None
    is_reachable: bool | None

    is_active: bool
    notes: str | None

    created_at: datetime
    updated_at: datetime

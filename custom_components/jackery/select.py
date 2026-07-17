"""Select platform for Jackery integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from socketry import MqttError

from .coordinator import JackeryCoordinator
from .entity import JackeryEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class JackerySelectEntityDescription(SelectEntityDescription):  # type: ignore[misc]
    """Describes a Jackery select entity."""

    property_key: str
    slug: str
    value_map: dict[int, str] | None = None
    option_to_value: dict[str, int] | None = None


SELECT_DESCRIPTIONS: tuple[JackerySelectEntityDescription, ...] = (
    JackerySelectEntityDescription(
        key="ast",
        translation_key="auto_shutdown",
        property_key="ast",
        slug="auto-shutdown",
        options=["Off", "2 h", "8 h", "12 h", "24 h"],
        value_map={0: "Off", 120: "2 h", 480: "8 h", 720: "12 h", 1440: "24 h"},
        option_to_value={"Off": 0, "2 h": 120, "8 h": 480, "12 h": 720, "24 h": 1440},
        entity_category=EntityCategory.CONFIG,
    ),
    JackerySelectEntityDescription(
        key="pm",
        translation_key="energy_saving",
        property_key="pm",
        slug="energy-saving",
        options=["Off", "2 h", "8 h", "12 h", "24 h"],
        value_map={0: "Off", 120: "2 h", 480: "8 h", 720: "12 h", 1440: "24 h"},
        option_to_value={"Off": 0, "2 h": 120, "8 h": 480, "12 h": 720, "24 h": 1440},
        entity_category=EntityCategory.CONFIG,
    ),
    JackerySelectEntityDescription(
        key="sltb",
        translation_key="screen_timeout",
        property_key="sltb",
        slug="screen-timeout",
        options=["Off", "2 min", "2 h"],
        value_map={1: "Off", 2: "2 min", 3: "2 h"},
        option_to_value={"Off": 1, "2 min": 2, "2 h": 3},
        entity_category=EntityCategory.CONFIG,
    ),
    JackerySelectEntityDescription(
        key="lm",
        translation_key="light_mode",
        property_key="lm",
        slug="light",
        options=["off", "low", "high", "sos"],
    ),
    JackerySelectEntityDescription(
        key="cs",
        translation_key="charge_speed",
        property_key="cs",
        slug="charge-speed",
        entity_category=EntityCategory.CONFIG,
        options=["fast", "mute"],
    ),
    JackerySelectEntityDescription(
        key="lps",
        translation_key="battery_protection",
        property_key="lps",
        slug="battery-protection",
        entity_category=EntityCategory.CONFIG,
        options=["full", "eco"],
    ),
)


class JackerySelectEntity(JackeryEntity, SelectEntity):  # type: ignore[misc]
    """Representation of a Jackery select."""

    entity_description: JackerySelectEntityDescription

    def __init__(
        self,
        coordinator: JackeryCoordinator,
        device_sn: str,
        description: JackerySelectEntityDescription,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, device_sn, description)

    @property
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        raw = self._prop(self.entity_description.property_key)
        if raw is None:
            return None
        try:
            raw_value = int(raw)  # type: ignore[call-overload]
        except (TypeError, ValueError):
            return None

        if self.entity_description.value_map is not None:
            return self.entity_description.value_map.get(raw_value)

        options = self.entity_description.options
        if options is None or raw_value < 0 or raw_value >= len(options):
            return None
        result: str = options[raw_value]
        return result

    async def async_select_option(self, option: str) -> None:
        """Set the selected option via socketry."""
        coordinator = self.coordinator
        sn = self._device_sn
        slug = self.entity_description.slug
        prop_key = self.entity_description.property_key

        if coordinator.client is None:
            return

        if self.entity_description.option_to_value is not None:
            int_value = self.entity_description.option_to_value.get(option)
            if int_value is None:
                return
        else:
            options = self.entity_description.options
            if options is None or option not in options:
                return
            int_value = options.index(option)

        try:
            device = coordinator.client.device(sn)
            await device.set_property(slug, int_value)
        except (KeyError, ValueError, MqttError) as err:
            _LOGGER.error("Failed to set %s=%s for device %s: %s", slug, option, sn, err)
            return

        # Optimistic update: reflect the expected device value
        if coordinator.data is not None and sn in coordinator.data:
            coordinator.data[sn][prop_key] = int_value
            coordinator.async_set_updated_data(coordinator.data)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Jackery select entities from a config entry."""
    coordinator: JackeryCoordinator = entry.runtime_data
    entities: list[JackerySelectEntity] = []

    for device in coordinator.devices:
        sn = str(device.get("devSn", ""))
        if not sn:
            continue
        device_data = coordinator.data.get(sn, {})
        for description in SELECT_DESCRIPTIONS:
            if description.property_key in device_data:
                entities.append(JackerySelectEntity(coordinator, sn, description))

    async_add_entities(entities)

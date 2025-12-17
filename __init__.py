import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.storage import Store
from .const import DOMAIN, STORAGE_KEY, STORAGE_VERSION
from .vehicle_store import VehicleStore

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    # Pro config flow integrace je lepší vrátit True a nechat práci na async_setup_entry
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    vehicle_store = VehicleStore(hass, store)
    
    # DŮLEŽITÉ: Načíst data z disku
    await vehicle_store.async_load()
    
    hass.data.setdefault(DOMAIN, vehicle_store)

    # Registrace služby add_refuel
    async def handle_add_refuel(call: ServiceCall):
        vehicle_id = call.data.get("vehicle_id")
        date = call.data.get("date") # Pozor: může přijít jako string nebo datetime objekt
        liters = call.data.get("liters")
        price_per_l = call.data.get("price_per_l")
        odometer = call.data.get("odometer")

        await vehicle_store.add_refuel(
            vehicle_id, str(date), liters, price_per_l, odometer
        )

    hass.services.async_register(DOMAIN, "add_refuel", handle_add_refuel)

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data.pop(DOMAIN)
    return unload_ok
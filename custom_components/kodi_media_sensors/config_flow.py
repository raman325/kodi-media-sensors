import logging
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.components.kodi.const import DOMAIN as KODI_DOMAIN
from homeassistant.core import callback

# from homeassistant.helpers import entity_registry, entity_platform
import voluptuous as vol

from .const import (
    OPTION_HIDE_WATCHED,
    OPTION_SEARCH_SONGS,
    OPTION_SEARCH_SONGS_LIMIT,
    OPTION_SEARCH_ALBUMS,
    OPTION_SEARCH_ALBUMS_LIMIT,
    OPTION_SEARCH_ARTISTS,
    OPTION_SEARCH_ARTISTS_LIMIT,
    OPTION_SEARCH_MOVIES,
    OPTION_SEARCH_MOVIES_LIMIT,
    OPTION_SEARCH_TVSHOWS,
    OPTION_SEARCH_TVSHOWS_LIMIT,
    OPTION_SEARCH_CHANNELS_TV,
    OPTION_SEARCH_CHANNELS_TV_LIMIT,
    OPTION_SEARCH_CHANNELS_RADIO,
    OPTION_SEARCH_CHANNELS_RADIO_LIMIT,
    OPTION_SEARCH_EPISODES,
    OPTION_SEARCH_EPISODES_LIMIT,
    OPTION_SEARCH_RECENT_LIMIT,
    OPTION_SEARCH_RECENT_SONGS,
    OPTION_SEARCH_RECENT_ALBUMS,
    OPTION_SEARCH_RECENT_MOVIES,
    OPTION_SEARCH_RECENT_EPISODES,
    OPTION_SEARCH_KEEP_ALIVE_TIMER,
    DEFAULT_OPTION_HIDE_WATCHED,
    DEFAULT_OPTION_SEARCH_SONGS,
    DEFAULT_OPTION_SEARCH_SONGS_LIMIT,
    DEFAULT_OPTION_SEARCH_ALBUMS,
    DEFAULT_OPTION_SEARCH_ALBUMS_LIMIT,
    DEFAULT_OPTION_SEARCH_ARTISTS,
    DEFAULT_OPTION_SEARCH_ARTISTS_LIMIT,
    DEFAULT_OPTION_SEARCH_CHANNELS_TV,
    DEFAULT_OPTION_SEARCH_CHANNELS_TV_LIMIT,
    DEFAULT_OPTION_SEARCH_CHANNELS_RADIO,
    DEFAULT_OPTION_SEARCH_CHANNELS_RADIO_LIMIT,
    DEFAULT_OPTION_SEARCH_MOVIES,
    DEFAULT_OPTION_SEARCH_MOVIES_LIMIT,
    DEFAULT_OPTION_SEARCH_TVSHOWS,
    DEFAULT_OPTION_SEARCH_TVSHOWS_LIMIT,
    DEFAULT_OPTION_SEARCH_EPISODES,
    DEFAULT_OPTION_SEARCH_EPISODES_LIMIT,
    DEFAULT_OPTION_SEARCH_RECENT_LIMIT,
    DEFAULT_OPTION_SEARCH_RECENT_SONGS,
    DEFAULT_OPTION_SEARCH_RECENT_ALBUMS,
    DEFAULT_OPTION_SEARCH_RECENT_MOVIES,
    DEFAULT_OPTION_SEARCH_RECENT_EPISODES,
    DEFAULT_OPTION_SEARCH_KEEP_ALIVE_TIMER,
    CONF_KODI_INSTANCE,
    DOMAIN,
    CONF_SENSOR_RECENTLY_ADDED_TVSHOW,
    CONF_SENSOR_RECENTLY_ADDED_MOVIE,
    CONF_SENSOR_PLAYLIST,
    CONF_SENSOR_SEARCH,
)

_LOGGER = logging.getLogger(__name__)


class KodiMediaSensorsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Kodi Media Sensors config flow."""

    async def async_step_user(self, user_input: Optional[Dict[str, Any]]):
        """Handle a flow initialized via the user interface."""
        # Find all configured kodi instances to allow the user to select one.
        kodi_instances: Dict[str, str] = {
            entry.entry_id: entry.title
            for entry in self.hass.config_entries.async_entries(KODI_DOMAIN)
            if entry.source != "ignore"
        }
        data_schema = vol.Schema(
            {
                vol.Required(CONF_KODI_INSTANCE): vol.In(list(kodi_instances.values())),
                vol.Optional(CONF_SENSOR_RECENTLY_ADDED_TVSHOW, default=False): bool,
                vol.Optional(CONF_SENSOR_RECENTLY_ADDED_MOVIE, default=False): bool,
                vol.Optional(CONF_SENSOR_PLAYLIST, default=False): bool,
                vol.Optional(CONF_SENSOR_SEARCH, default=False): bool,
            }
        )

        errors = {}
        if not kodi_instances:
            errors["base"] = "kodi_not_configured"

        if user_input is not None:
            config_entry_id: Optional[str] = None
            for entry_id, title in kodi_instances.items():
                if title == user_input[CONF_KODI_INSTANCE]:
                    config_entry_id = entry_id
                    break
            if config_entry_id is None:
                errors["base"] = "kodi_not_configured"

            if not errors:
                return self.async_create_entry(
                    title="Kodi Media Sensors",
                    data={
                        CONF_KODI_INSTANCE: config_entry_id,
                        CONF_SENSOR_RECENTLY_ADDED_TVSHOW: user_input[
                            CONF_SENSOR_RECENTLY_ADDED_TVSHOW
                        ],
                        CONF_SENSOR_RECENTLY_ADDED_MOVIE: user_input[
                            CONF_SENSOR_RECENTLY_ADDED_MOVIE
                        ],
                        CONF_SENSOR_PLAYLIST: user_input[CONF_SENSOR_PLAYLIST],
                        CONF_SENSOR_SEARCH: user_input[CONF_SENSOR_SEARCH],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handles options flow for the component."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema_base = {}

        sensor_recent_movie_active = self.config_entry.data.get(
            CONF_SENSOR_RECENTLY_ADDED_MOVIE
        )
        sensor_recent_tvshow_active = self.config_entry.data.get(
            CONF_SENSOR_RECENTLY_ADDED_TVSHOW
        )
        sensor_search_active = self.config_entry.data.get(CONF_SENSOR_SEARCH)

        if (
            sensor_recent_movie_active is not None
            and str(sensor_recent_movie_active) == "True"
        ) or (
            sensor_recent_tvshow_active is not None
            and str(sensor_recent_tvshow_active) == "True"
        ):
            schema_base = self.add_to_schema(
                OPTION_HIDE_WATCHED,
                DEFAULT_OPTION_HIDE_WATCHED,
                bool,
                schema_base,
            )

        if sensor_search_active is not None and str(sensor_search_active) == "True":
            # SEARCH SONGS
            schema_base = self.add_to_schema(
                OPTION_SEARCH_SONGS,
                DEFAULT_OPTION_SEARCH_SONGS,
                bool,
                schema_base,
            )
            schema_base = self.add_to_schema(
                OPTION_SEARCH_SONGS_LIMIT,
                DEFAULT_OPTION_SEARCH_SONGS_LIMIT,
                int,
                schema_base,
            )

            # SEARCH ALBUMS
            schema_base = self.add_to_schema(
                OPTION_SEARCH_ALBUMS,
                DEFAULT_OPTION_SEARCH_ALBUMS,
                bool,
                schema_base,
            )
            schema_base = self.add_to_schema(
                OPTION_SEARCH_ALBUMS_LIMIT,
                DEFAULT_OPTION_SEARCH_ALBUMS_LIMIT,
                int,
                schema_base,
            )

            # SEARCH ARTISTS
            schema_base = self.add_to_schema(
                OPTION_SEARCH_ARTISTS,
                DEFAULT_OPTION_SEARCH_ARTISTS,
                bool,
                schema_base,
            )
            schema_base = self.add_to_schema(
                OPTION_SEARCH_ARTISTS_LIMIT,
                DEFAULT_OPTION_SEARCH_ARTISTS_LIMIT,
                int,
                schema_base,
            )

            # SEARCH MOVIES
            schema_base = self.add_to_schema(
                OPTION_SEARCH_MOVIES,
                DEFAULT_OPTION_SEARCH_MOVIES,
                bool,
                schema_base,
            )
            schema_base = self.add_to_schema(
                OPTION_SEARCH_MOVIES_LIMIT,
                DEFAULT_OPTION_SEARCH_MOVIES_LIMIT,
                int,
                schema_base,
            )

            # SEARCH TVSHOWS
            schema_base = self.add_to_schema(
                OPTION_SEARCH_TVSHOWS,
                DEFAULT_OPTION_SEARCH_TVSHOWS,
                bool,
                schema_base,
            )
            schema_base = self.add_to_schema(
                OPTION_SEARCH_TVSHOWS_LIMIT,
                DEFAULT_OPTION_SEARCH_TVSHOWS_LIMIT,
                int,
                schema_base,
            )

            # SEARCH EPISODES
            schema_base = self.add_to_schema(
                OPTION_SEARCH_EPISODES,
                DEFAULT_OPTION_SEARCH_EPISODES,
                bool,
                schema_base,
            )
            schema_base = self.add_to_schema(
                OPTION_SEARCH_EPISODES_LIMIT,
                DEFAULT_OPTION_SEARCH_EPISODES_LIMIT,
                int,
                schema_base,
            )

            # SEARCH CHANNELS TV
            schema_base = self.add_to_schema(
                OPTION_SEARCH_CHANNELS_TV,
                DEFAULT_OPTION_SEARCH_CHANNELS_TV,
                bool,
                schema_base,
            )
            schema_base = self.add_to_schema(
                OPTION_SEARCH_CHANNELS_TV_LIMIT,
                DEFAULT_OPTION_SEARCH_CHANNELS_TV_LIMIT,
                int,
                schema_base,
            )

            # SEARCH CHANNELS RADIO
            schema_base = self.add_to_schema(
                OPTION_SEARCH_CHANNELS_RADIO,
                DEFAULT_OPTION_SEARCH_CHANNELS_RADIO,
                bool,
                schema_base,
            )
            schema_base = self.add_to_schema(
                OPTION_SEARCH_CHANNELS_RADIO_LIMIT,
                DEFAULT_OPTION_SEARCH_CHANNELS_RADIO_LIMIT,
                int,
                schema_base,
            )

            # SEARCH RECENTS
            schema_base = self.add_to_schema(
                OPTION_SEARCH_RECENT_SONGS,
                DEFAULT_OPTION_SEARCH_RECENT_SONGS,
                bool,
                schema_base,
            )
            schema_base = self.add_to_schema(
                OPTION_SEARCH_RECENT_ALBUMS,
                DEFAULT_OPTION_SEARCH_RECENT_ALBUMS,
                bool,
                schema_base,
            )
            schema_base = self.add_to_schema(
                OPTION_SEARCH_RECENT_MOVIES,
                DEFAULT_OPTION_SEARCH_RECENT_MOVIES,
                bool,
                schema_base,
            )
            schema_base = self.add_to_schema(
                OPTION_SEARCH_RECENT_EPISODES,
                DEFAULT_OPTION_SEARCH_RECENT_EPISODES,
                bool,
                schema_base,
            )

            schema_base = self.add_to_schema(
                OPTION_SEARCH_RECENT_LIMIT,
                DEFAULT_OPTION_SEARCH_RECENT_LIMIT,
                int,
                schema_base,
            )
            schema_base = self.add_to_schema(
                OPTION_SEARCH_KEEP_ALIVE_TIMER,
                DEFAULT_OPTION_SEARCH_KEEP_ALIVE_TIMER,
                int,
                schema_base,
            )

        schema_full = vol.Schema(schema_base)
        return self.async_show_form(
            step_id="init",
            data_schema=schema_full,
        )

    def add_to_schema(self, option, default, value_type, schema):
        option_value = self.config_entry.options.get(option, default)
        if value_type == bool:
            schema[vol.Optional(option, default=option_value)] = bool

        elif value_type == int:
            schema[vol.Optional(option, default=option_value)] = int

        return schema

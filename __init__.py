"""Dump Loaded Album"""

# Copyright (C) 2026 Bob Swift (rdswift)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.


import json
import os

from PyQt6 import QtWidgets

from picard.plugin3.api import (
    Album,
    Metadata,
    OptionsPage,
    PluginApi,
    t_,
)
from picard.util import make_filename_from_title

from .ui_options_dump_loaded_album import Ui_DumpLoadedAlbumOptionsPage


USER_GUIDE_URL = 'https://picard-plugins-user-guides.readthedocs.io/en/latest/dump_loaded_album/user_guide.html'

# Option settings
OPT_TARGET_DIR = 'target_directory'


def dump_album(api: PluginApi, _album: Album, _album_metadata: Metadata, release_node: dict) -> None:
    """Process album artists.

    Args:
        api (PluginApi): The plugin API object.
        _album (Album): The Album object to use for the processing.
        _album_metadata (Metadata): Metadata object for the album.
        release_node (dict): Dictionary of release data from MusicBrainz api.
    """
    album_title = release_node['title'] if 'title' in release_node else 'Unknown Title'
    filename = make_filename_from_title(f"Album={album_title}.json")
    filepath = os.path.join(api.plugin_config[OPT_TARGET_DIR], filename)
    try:
        with open(filepath, 'w', encoding='utf8') as f:
            json.dump(release_node, f, indent=4, sort_keys=True)
        api.logger.debug(f"Exported album file: {filepath}")
    except (TypeError, RecursionError, ValueError) as err:
        api.logger.error(f"Error exporting \"{filepath}\" ({err})")


class DumpLoadedAlbumOptionsPage(OptionsPage):
    """Options page for the Dump Loaded Album plugin.
    """

    TITLE = t_("ui.title", "Dump Loaded Album")
    HELP_URL = USER_GUIDE_URL

    def __init__(self, parent=None) -> None:
        super(DumpLoadedAlbumOptionsPage, self).__init__(parent)

        self.ui = Ui_DumpLoadedAlbumOptionsPage()
        self.ui.setupUi(self)

        icon = self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DirOpenIcon)
        self.ui.b_select_target_dir.setIcon(icon)
        self.ui.b_select_target_dir.clicked.connect(self.select_target_dir)

        self.api = PluginApi.get_api()

        # self.user_documents_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)

    def load(self) -> None:
        """Load the option settings.
        """
        self.ui.target_dir.setText(self.api.plugin_config[OPT_TARGET_DIR])

    def save(self) -> None:
        """Save the option settings.
        """
        self.api.plugin_config[OPT_TARGET_DIR] = self.ui.target_dir.text()

    def select_target_dir(self) -> None:
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            self.api.tr('ui.select_directory', 'Select Plugin Root Directory'),
            self.ui.target_dir.text().strip() or os.path.expanduser('~'),
            QtWidgets.QFileDialog.Option.ShowDirsOnly,
        )
        if directory:
            self.ui.target_dir.setText(os.path.normpath(directory))


def enable(api: PluginApi) -> None:
    """Called when the plugin is enabled.

    Args:
        api (PluginApi): The api for the plugin.
    """
    # Initialize settings
    api.plugin_config.register_option(OPT_TARGET_DIR, os.path.expanduser('~'))

    api.register_options_page(DumpLoadedAlbumOptionsPage)

    # Register the plugin to run at a high priority.
    api.register_album_metadata_processor(dump_album, priority=100)

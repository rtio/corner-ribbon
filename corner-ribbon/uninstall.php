<?php
// Copyright (C) 2026 Rafael Meneses
// SPDX-License-Identifier: GPL-2.0-or-later
/** Delete only this site's ribbon setting on uninstall. @package CornerRibbon */

defined( 'WP_UNINSTALL_PLUGIN' ) || exit;

delete_option( 'rtio_corner_ribbon' );

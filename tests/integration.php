<?php
// Copyright (C) 2026 Rafael Meneses
// SPDX-License-Identifier: GPL-2.0-or-later
/** Run with wp eval-file against a disposable WordPress installation. */

if ( ! function_exists( 'rtio_cr_settings' ) ) {
	WP_CLI::error( 'Corner Ribbon must be active before these behavioral checks can pass.' );
}

$checks = 0;
$check = function ( $condition, $message ) use ( &$checks ) {
	if ( ! $condition ) {
		WP_CLI::error( $message );
	}
	++$checks;
};
$original = get_option( 'rtio_corner_ribbon', null );

try {
	delete_option( 'rtio_corner_ribbon' );
	$defaults = rtio_cr_settings();
	$check( 'R.I.P. ERIC' === $defaults['text'], 'Default tribute wording.' );
	$check( '#00e49a' === $defaults['accent'], 'Default uses the Beep mint accent.' );
	$check( '#000000' === $defaults['background'], 'Default uses a black band.' );

	// Exercise real Settings API registration and option sanitization.
	require_once WP_PLUGIN_DIR . '/rtio-corner-ribbon/includes/settings.php';
	rtio_cr_register_settings();
	update_option( 'rtio_corner_ribbon', array( 'enabled' => '1', 'text' => '<b>In memory</b>', 'accent' => 'red; } body { display:none', 'background' => '#123456', 'url' => 'javascript:alert(1)' ) );
	$settings = rtio_cr_settings();
	$check( 'In memory' === $settings['text'], 'HTML is stripped from the label.' );
	$check( '#00e49a' === $settings['accent'], 'Invalid CSS color falls back safely.' );
	$check( '#123456' === $settings['background'], 'Valid colors survive saving.' );
	$check( '' === $settings['url'], 'JavaScript URLs are rejected.' );
	$check( '' === rtio_cr_sanitize( array( 'url' => 'mailto:test@example.test' ) )['url'], 'Non-web URL schemes are rejected.' );
	$check( '' === rtio_cr_sanitize( array( 'url' => '//example.test' ) )['url'], 'Protocol-relative URLs are rejected.' );

	$malformed = rtio_cr_sanitize( array( 'enabled' => array( 1 ), 'text' => array( '<script>' ), 'accent' => array( '#fff' ), 'background' => new stdClass(), 'url' => array( 'https://example.test' ) ) );
	$check( false === $malformed['enabled'] && '' === $malformed['text'] && '' === $malformed['url'], 'Malformed values do not crash or enable the ribbon.' );
	$check( false === rtio_cr_sanitize( 'invalid' )['enabled'], 'Malformed root options are disabled.' );
	$check( 24 === mb_strlen( rtio_cr_sanitize( array( 'text' => str_repeat( 'á', 30 ) ) )['text'] ), 'Long Unicode labels are bounded safely.' );

	update_option( 'rtio_corner_ribbon', array( 'enabled' => 0, 'text' => 'Hidden' ) );
	ob_start();
	do_action( 'wp_body_open' );
	$check( '' === ob_get_clean(), 'Disabled ribbons produce no markup.' );
	update_option( 'rtio_corner_ribbon', array( 'enabled' => 1, 'text' => '   ' ) );
	ob_start();
	do_action( 'wp_body_open' );
	$check( '' === ob_get_clean(), 'Blank labels produce no markup.' );

	update_option( 'rtio_corner_ribbon', array( 'enabled' => 1, 'text' => 'Remember "Eric" & all', 'url' => 'https://example.test/tribute?a=1&b=2' ) );
	ob_start();
	do_action( 'wp_body_open' );
	do_action( 'wp_footer' );
	$output = ob_get_clean();
	$check( 1 === substr_count( $output, 'id="rtio-corner-ribbon"' ), 'Body and footer hooks render exactly once.' );
	$check( false !== strpos( $output, 'Remember &quot;Eric&quot; &amp; all' ), 'Visible text is escaped.' );
	$check( false !== strpos( $output, '<a ' ) && false !== strpos( $output, 'https://example.test/tribute' ), 'A configured tribute URL creates a semantic link.' );
	$check( false === strpos( $output, 'target="_blank"' ), 'The link uses normal same-tab navigation.' );

	$subscriber = wp_insert_user( array( 'user_login' => 'qa-ribbon-subscriber', 'user_pass' => wp_generate_password(), 'role' => 'subscriber' ) );
	if ( is_wp_error( $subscriber ) ) {
		$subscriber = get_user_by( 'login', 'qa-ribbon-subscriber' )->ID;
	}
	wp_set_current_user( $subscriber );
	$check( ! current_user_can( 'manage_options' ), 'Subscriber cannot manage plugin settings.' );
	WP_CLI::success( $checks . ' integration assertions passed.' );
} finally {
	if ( null === $original ) {
		delete_option( 'rtio_corner_ribbon' );
	} else {
		update_option( 'rtio_corner_ribbon', $original );
	}
}

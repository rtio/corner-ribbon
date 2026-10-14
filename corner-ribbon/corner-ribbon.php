<?php
// Copyright (C) 2026 Rafael Meneses
// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * Plugin Name: RTIO Corner Ribbon
 * Plugin URI: https://github.com/rtio/corner-ribbon
 * Description: A quiet diagonal tribute ribbon with editable wording, colors, and an optional link.
 * Version: 1.1.2
 * Author: Rafael Meneses
 * Author URI: https://rtio.dev/
 * Requires at least: 6.0
 * Requires PHP: 7.4
 * License: GPL-2.0-or-later
 * License URI: https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain: rtio-corner-ribbon
 *
 * @package CornerRibbon
 */

defined( 'ABSPATH' ) || exit;

/** Defaults match the Beep theme's black and mint palette. */
function rtio_cr_defaults() {
	return array(
		'enabled'    => true,
		'text'       => 'R.I.P. ERIC',
		'accent'     => '#00e49a',
		'background' => '#000000',
		'url'        => '',
	);
}

/** Normalize both form submissions and stored values before use. */
function rtio_cr_sanitize( $input ) {
	$defaults = rtio_cr_defaults();
	$input    = is_array( $input ) ? $input : array();
	$text     = isset( $input['text'] ) && is_string( $input['text'] ) ? sanitize_text_field( $input['text'] ) : '';
	$url      = isset( $input['url'] ) && is_string( $input['url'] ) ? trim( $input['url'] ) : '';
	$url      = preg_match( '#^https?://#i', $url ) ? esc_url_raw( $url, array( 'http', 'https' ) ) : '';
	$url      = wp_parse_url( $url, PHP_URL_HOST ) ? $url : '';
	$output   = array(
		'enabled' => isset( $input['enabled'] ) && in_array( $input['enabled'], array( true, 1, '1' ), true ),
		'text'    => mb_substr( $text, 0, 24 ),
		'url'     => $url,
	);
	foreach ( array( 'accent', 'background' ) as $color ) {
		$value            = isset( $input[ $color ] ) && is_string( $input[ $color ] ) ? sanitize_hex_color( $input[ $color ] ) : null;
		$output[ $color ] = $value ? strtolower( $value ) : $defaults[ $color ];
	}
	return $output;
}

/** Get only validated settings, including when updated through WP-CLI. */
function rtio_cr_settings() {
	return rtio_cr_sanitize( get_option( 'rtio_corner_ribbon', rtio_cr_defaults() ) );
}

/** Keep the ribbon out of feeds, embeds, and the dashboard. */
function rtio_cr_is_visible() {
	$settings = rtio_cr_settings();
	return ! is_admin() && ! is_feed() && ! is_embed() && $settings['enabled'] && '' !== $settings['text'];
}

function rtio_cr_enqueue() {
	if ( ! rtio_cr_is_visible() ) {
		return;
	}
	wp_enqueue_style( 'rtio-corner-ribbon', plugins_url( 'assets/ribbon.css', __FILE__ ), array(), '1.1.2' );
}
add_action( 'wp_enqueue_scripts', 'rtio_cr_enqueue' );

/** Render once, even if a theme calls both body-open and footer hooks. */
function rtio_cr_render() {
	static $rendered = false;
	if ( $rendered || ! rtio_cr_is_visible() ) {
		return;
	}
	$rendered = true;
	$settings = rtio_cr_settings();
	$style    = '--rtio-cr-accent:' . $settings['accent'] . ';--rtio-cr-background:' . $settings['background'] . ';';
	$tag      = $settings['url'] ? 'a' : 'span';
	$length   = mb_strlen( $settings['text'] );
	$class    = 'rtio-cr-band' . ( $length > 14 ? ' rtio-cr-band--long' : '' );
	?>
	<div id="rtio-corner-ribbon" class="rtio-corner-ribbon" style="<?php echo esc_attr( $style ); ?>">
		<<?php echo $tag; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Fixed a/span allowlist. ?> class="<?php echo esc_attr( $class ); ?>"<?php if ( $settings['url'] ) : ?> href="<?php echo esc_url( $settings['url'] ); ?>"<?php endif; ?>><?php echo esc_html( $settings['text'] ); ?></<?php echo $tag; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Fixed a/span allowlist. ?>>
	</div>
	<?php
}
add_action( 'wp_body_open', 'rtio_cr_render', 5 );
add_action( 'wp_footer', 'rtio_cr_render', 5 );

/** Mobile clearance also works for themes that only call wp_footer. */
function rtio_cr_body_class( $classes ) {
	if ( rtio_cr_is_visible() ) {
		$classes[] = 'rtio-cr-active';
	}
	return $classes;
}
add_filter( 'body_class', 'rtio_cr_body_class' );

function rtio_cr_action_links( $links ) {
	array_unshift( $links, '<a href="' . esc_url( admin_url( 'options-general.php?page=corner-ribbon' ) ) . '">' . esc_html__( 'Settings', 'rtio-corner-ribbon' ) . '</a>' );
	return $links;
}
add_filter( 'plugin_action_links_' . plugin_basename( __FILE__ ), 'rtio_cr_action_links' );

if ( is_admin() ) {
	require_once __DIR__ . '/includes/settings.php';
}

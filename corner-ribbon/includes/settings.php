<?php
// Copyright (C) 2026 Rafael Meneses
// SPDX-License-Identifier: GPL-2.0-or-later
/** Settings screen and registration. @package CornerRibbon */

defined( 'ABSPATH' ) || exit;

function rtio_cr_register_settings() {
	register_setting(
		'rtio_corner_ribbon',
		'rtio_corner_ribbon',
		array(
			'type'              => 'array',
			'sanitize_callback' => 'rtio_cr_sanitize',
			'default'           => rtio_cr_defaults(),
		)
	);
	add_settings_section( 'rtio_cr_appearance', '', '__return_false', 'corner-ribbon' );
	$fields = array(
		'enabled'    => __( 'Visibility', 'corner-ribbon' ),
		'text'       => __( 'Name or message', 'corner-ribbon' ),
		'accent'     => __( 'Text and border color', 'corner-ribbon' ),
		'background' => __( 'Background color', 'corner-ribbon' ),
		'url'        => __( 'Link URL (optional)', 'corner-ribbon' ),
	);
	foreach ( $fields as $key => $label ) {
		add_settings_field( $key, $label, 'rtio_cr_field', 'corner-ribbon', 'rtio_cr_appearance', array( 'label_for' => 'rtio-cr-' . $key, 'key' => $key ) );
	}
}
add_action( 'admin_init', 'rtio_cr_register_settings' );

function rtio_cr_menu() {
	add_options_page( __( 'Corner Ribbon', 'corner-ribbon' ), __( 'Corner Ribbon', 'corner-ribbon' ), 'manage_options', 'corner-ribbon', 'rtio_cr_page' );
}
add_action( 'admin_menu', 'rtio_cr_menu' );

/** Use WordPress's color controls only on this plugin's settings screen. */
function rtio_cr_admin_assets( $hook ) {
	if ( 'settings_page_corner-ribbon' !== $hook ) {
		return;
	}
	wp_enqueue_style( 'wp-color-picker' );
	wp_enqueue_script( 'rtio-cr-settings', plugins_url( 'assets/settings.js', dirname( __DIR__ ) . '/corner-ribbon.php' ), array( 'wp-color-picker' ), '1.1.0', true );
}
add_action( 'admin_enqueue_scripts', 'rtio_cr_admin_assets' );

function rtio_cr_field( $args ) {
	$settings = rtio_cr_settings();
	$defaults = rtio_cr_defaults();
	$key      = $args['key'];
	$id       = 'rtio-cr-' . $key;
	$name     = 'rtio_corner_ribbon[' . $key . ']';
	if ( 'enabled' === $key ) {
		?>
		<label><input type="checkbox" id="<?php echo esc_attr( $id ); ?>" name="<?php echo esc_attr( $name ); ?>" value="1" <?php checked( $settings['enabled'] ); ?>> <?php esc_html_e( 'Show the ribbon on the website', 'corner-ribbon' ); ?></label>
		<?php
	} elseif ( 'text' === $key ) {
		?>
		<input class="regular-text" type="text" id="<?php echo esc_attr( $id ); ?>" name="<?php echo esc_attr( $name ); ?>" value="<?php echo esc_attr( $settings[ $key ] ); ?>" maxlength="24" aria-describedby="rtio-cr-text-help">
		<p class="description" id="rtio-cr-text-help"><?php esc_html_e( 'Enter the full wording, for example R.I.P. ERIC. Up to 24 characters. Leave blank to hide the ribbon.', 'corner-ribbon' ); ?></p>
		<?php
	} elseif ( 'url' === $key ) {
		?>
		<input class="regular-text" type="url" id="<?php echo esc_attr( $id ); ?>" name="<?php echo esc_attr( $name ); ?>" value="<?php echo esc_attr( $settings[ $key ] ); ?>" placeholder="https://" aria-describedby="rtio-cr-url-help">
		<p class="description" id="rtio-cr-url-help"><?php esc_html_e( 'An https:// or http:// address. Leave blank for a ribbon without a link.', 'corner-ribbon' ); ?></p>
		<?php
	} else {
		?>
		<input class="regular-text rtio-cr-color" type="text" id="<?php echo esc_attr( $id ); ?>" name="<?php echo esc_attr( $name ); ?>" value="<?php echo esc_attr( $settings[ $key ] ); ?>" data-default-color="<?php echo esc_attr( $defaults[ $key ] ); ?>" pattern="#[a-fA-F0-9]{3}([a-fA-F0-9]{3})?" maxlength="7" aria-describedby="<?php echo esc_attr( $id . '-help' ); ?>">
		<p class="description" id="<?php echo esc_attr( $id . '-help' ); ?>"><?php esc_html_e( 'A hex color, such as #00e49a or #000000. Choose colors with clear contrast.', 'corner-ribbon' ); ?></p>
		<?php
	}
}

function rtio_cr_page() {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}
	?>
	<div class="wrap">
		<h1><?php esc_html_e( 'Corner Ribbon', 'corner-ribbon' ); ?></h1>
		<p><?php esc_html_e( 'A diagonal tribute in the upper-left corner. The ribbon scrolls with the page and leaves room above the header on small screens.', 'corner-ribbon' ); ?></p>
		<form action="options.php" method="post">
			<?php
			settings_fields( 'rtio_corner_ribbon' );
			do_settings_sections( 'corner-ribbon' );
			submit_button();
			?>
		</form>
	</div>
	<?php
}

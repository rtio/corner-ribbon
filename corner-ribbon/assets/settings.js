/* Copyright (C) 2026 Rafael Meneses; SPDX-License-Identifier: GPL-2.0-or-later */
/* WordPress supplies the picker. Plain hex inputs work without JavaScript. */
jQuery(function ($) {
	$('.rtio-cr-color').each(function () {
		var label = $('label[for="' + this.id + '"]').text();
		$(this).wpColorPicker().closest('.wp-picker-container')
			.find('.wp-color-result').attr('aria-label', label);
	});
});

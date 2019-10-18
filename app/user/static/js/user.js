$(document).ready(function() {
	$(function () {
		var timer = null;
		var xhr = null;
		$('.user-popup').hover(
			function (event) {
				// mouse in event handler
				var elem = $(event.currentTarget);
				timer = setTimeout(function () {
					timer = null;
					elem.popover({
						trigger: 'manual',
						html: true,
						container: elem,
						content: function() {
							var div_id =  "id-" + $.now();
							return popoverContent(div_id);
						}
					}).popover('show');

					function popoverContent(div_id) {
						var content = '<div id="'+ div_id +'">Loading...</div>';
						xhr = $.ajax('/user/' + elem.find('a:first').text().trim() + '/popup')
							.done(function (data) {
								$('#'+div_id).html(data);
							});
						return content;
					}
				}, 10);
			},
			function (event) {
				// mouse out event handler
				var elem = $(event.currentTarget);
				if (timer) {
					clearTimeout(timer);
					timer = null;
				}
				if (xhr) {
					xhr.abort();
					xhr = null;
				}

				elem.popover('dispose');
			}
		)
	});
});
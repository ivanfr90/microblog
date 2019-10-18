
function setMessageCount(n) {
	$('#message-count').text(n);
	$('#message-count').css('display', n ? 'inline-block' : 'none');
};
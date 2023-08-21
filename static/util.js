function get_game_data(key, parser = f => f) {
    return parser($("#game_data").data(key));
}

function set_game_data(key, value) {
    return $("#game_data").data(key, value);
}

function time_elapse_text() {
    const elapse = Date.now() - start_time;
    const seconds = elapse / 1000 % 60;
    const minutes = Math.floor(elapse / 60_000);
    return (minutes.toString().padStart(2, '0')) + " นาที " + ((seconds).toFixed(3)).padStart(6, '0') + " วินาที";
}

$.fn.preload = function () {
    this.each(function () {
        $('<img alt="" src=""/>')[0].src = this;
    });
}
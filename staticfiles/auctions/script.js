// Code for navigation bar
let burger = document.getElementById('burger');
let nav = document.getElementById('nav-links');

burger.addEventListener('click', () => {
    nav.classList.toggle('nav-active');
});

// Countdown Timer
setInterval(() => {
    var timers = document.querySelectorAll('.timer-values')
    for(var i = 0; i < timers.length; i++) {
        var day = parseInt(timers[i].children[0].textContent)
        var hour = parseInt(timers[i].children[1].textContent)
        var min = parseInt(timers[i].children[2].textContent)
        var sec = parseInt(timers[i].children[3].textContent)

        if(sec != 0) {
            sec--;
        }
        if(day != 0 || hour != 0 || min != 0 || sec != 0) {
            if(sec === 0) {
                min--;
                sec = 59;
                if(min === 0) {
                    hour--;
                    min = 59;
                    if(hour === 0) {
                        day--;
                        hour = 23;
                        if(day === 0) {
                            day = 0;
                        }
                    }
                }
            }
        }
        else {
            day = 0;
            hour = 0;
            min = 0;
            sec = 0;
        }

        if(day < 10) {
            day = '0' + day
        }
        if(hour < 10) {
            hour = '0' + hour
        }
        if(min < 10) {
            min = '0' + min
        }
        if(sec < 10) {
            sec = '0' + sec
        }

 
        timers[i].children[0].textContent = day
        timers[i].children[1].textContent = hour
        timers[i].children[2].textContent = min
        timers[i].children[3].textContent = sec
    }
    
}, 1000);
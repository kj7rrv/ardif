sender = document.querySelector('#sender')
sender.value = localStorage.getItem('mycallsign') || ''
sender.addEventListener('change', function() {
localStorage.setItem('mycallsign', sender.value)
})

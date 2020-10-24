button = document.querySelector('#copy')
input = document.querySelector('#data')
button.style = ''
input.style = 'display: none'
button.addEventListener('click', function(e) {
    e.preventDefault()
    input.style = ''
    input.select()
    input.setSelectionRange(0, 9999999999999999)
    document.execCommand("copy")
    input.style = 'display: none'
    }
)

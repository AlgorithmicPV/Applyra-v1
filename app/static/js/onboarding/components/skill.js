document.body.addEventListener("htmx:afterSwap", function(event) {
  initialize();
});

const initialize = () => {
  const cards = document.getElementsByClassName('card')

  for (let i = 0; i < cards.length; i++) {
    const editCont = cards[i].querySelector('#edit-cont')
    const editBtn = cards[i].querySelector('#edit-btn')
    const cancelBtn = cards[i].querySelector('#cancel-btn')
    const staticCertificateName = cards[i].querySelector('.name')

    editBtn.addEventListener('click', () => {
      staticCertificateName.style.display = 'none'
      editCont.style.display = 'flex'
      editBtn.style.display = 'none'
      cancelBtn.style.display = 'inline'
    })

    cancelBtn.addEventListener('click', () => {
      staticCertificateName.style.display = 'block'
      editCont.style.display = 'none'
      editBtn.style.display = 'inline'
      cancelBtn.style.display = 'none'
    })
  }
}

initialize();

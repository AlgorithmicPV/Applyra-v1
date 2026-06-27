document.body.addEventListener("htmx:afterSwap", function(event) {
  initialize();
});

const initialize = () => {
  const staticCertificateName = document.getElementById('static-certificate-name')
  const staticTime = document.getElementById('static-time')
  const editCont = document.getElementById('edit-cont')
  const editBtn = document.getElementById('edit-btn')
  const cancelBtn = document.getElementById('cancel-btn')


  editBtn.addEventListener('click', () => {
    staticCertificateName.style.display = 'none'
    staticTime.style.display = 'none'
    editCont.style.display = 'flex'
    editBtn.style.display = 'none'
    cancelBtn.style.display = 'inline'
  })


  cancelBtn.addEventListener('click', () => {
    staticCertificateName.style.display = 'block'
    staticTime.style.display = 'block'
    editCont.style.display = 'none'
    editBtn.style.display = 'inline'
    cancelBtn.style.display = 'none'
  })

}

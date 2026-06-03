const submitBtn = document.getElementById('submit-btn')
const fileInput = document.getElementById('file-input')


submitBtn.addEventListener('click', () => {
  fileInput.click()
})


fileInput.addEventListener('change', async () => {
  fileInput.form.submit()
})


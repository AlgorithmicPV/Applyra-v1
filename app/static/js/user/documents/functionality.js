const selectedFont = document.getElementById('selected-font')
const selections = document.getElementById('selections')


isSelectionHide = true


selectedFont.addEventListener('click', () => {
  if (isSelectionHide) {
    selections.style.display = "flex"
    isSelectionHide = false
  } else {
    selections.style.display = "none"
    isSelectionHide = true
  }
})



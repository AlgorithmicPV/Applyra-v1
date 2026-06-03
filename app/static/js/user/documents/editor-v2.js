import { Editor } from 'https://esm.sh/@tiptap/core'
import StarterKit from 'https://esm.sh/@tiptap/starter-kit'
import { Focus, Selection } from 'https://esm.sh/@tiptap/extensions'
import { FontSize, TextStyle, FontFamily } from 'https://esm.sh/@tiptap/extension-text-style'
import { Markdown } from 'https://esm.sh/@tiptap/markdown'


const editor = () => {
  const workspace = document.getElementById('workspace')

  if (!workspace) { return }

  const raw = document.getElementById("initial-data").textContent;

  const user = JSON.parse(raw);

  console.log(user);

  const boldBtn = document.getElementById('bold-btn')
  const italicBtn = document.getElementById('italic-btn')
  const underlineBtn = document.getElementById('underline-btn')
  const fontSizeInputBox = document.getElementById('font-size')
  const selections = document.getElementById('selections')
  const selectedFont = document.getElementById('selected-font')

  let fontSize = 16
  const navKeys = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown']
  let font
  let isSelectionHide = true


  let editor = new Editor({
    element: workspace,
    extensions: [
      StarterKit,
      FontSize,
      TextStyle,
      FontFamily,
      Markdown,
      Focus.configure({
        className: 'has-focus',
        mode: 'all',
      }),
      Selection.configure({
        className: 'selection',
      }),
    ],
    autofocus: true,
    shouldRerenderOnTransaction: true,
    immediatelyRender: true,
  })


  editor.commands.setFontSize(`${fontSize}px`)
  const docPage = document.querySelector('.tiptap')


  const boldbtnActivated = () => {
    if (editor.isActive('bold')) {
      boldBtn.classList.add('active')
    } else {
      boldBtn.classList.remove('active')
    }
  }


  const italicbtnActivated = () => {
    if (editor.isActive('italic')) {
      italicBtn.classList.add('active')
    } else {
      italicBtn.classList.remove('active')
    }
  }


  const underlineBtnActivated = () => {
    if (editor.isActive('underline')) {
      underlineBtn.classList.add('active')
    } else {
      underlineBtn.classList.remove('active')
    }
  }


  const updateFontSize = () => {
    if (fontSize == '') return // If user clicks somewhere except the text, there would be no font size, so if it is true, it will return and stop the rest of the function
    fontSizeInputBox.value = parseFloat(fontSize) // Convert the px value to an int
  }


  const updateFontStyle = () => {
    boldbtnActivated();
    underlineBtnActivated();
    italicbtnActivated();
  }


  const getElementAtCursor = () => {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
      let node = selection.anchorNode
      return node.nodeType === 3 ? node.parentNode : node;
    }
    return null;
  }


  const toggleHideShowSelection = () => {
    if (isSelectionHide) {
      selections.classList.remove("hidden")
      isSelectionHide = false
    } else {
      selections.classList.add("hidden")
      isSelectionHide = true
    }
  }


  document.addEventListener('keydown', (event) => {
    if (event.ctrlKey) {
      if (event.key.toLowerCase() === 'b') {
        boldbtnActivated();
      } else if (event.key.toLowerCase() === 'i') {
        italicbtnActivated();
      } else if (event.key.toLowerCase() === 'u') {
        underlineBtnActivated();
      }
    }
  })


  selections.addEventListener('click', (event) => {
    let clickedFontFamily = event.target
    font = clickedFontFamily.dataset.value;
    console.log(font)
    editor.chain().focus().setFontFamily(font).run()
    selectedFont.querySelector('span').innerText = event.target.innerText
    toggleHideShowSelection()
  })


  boldBtn.addEventListener('click', () => {
    editor.chain().focus().toggleBold().run()
    boldbtnActivated();
  })


  italicBtn.addEventListener('click', () => {
    editor.chain().focus().toggleItalic().run()
    italicbtnActivated()
  })


  underlineBtn.addEventListener('click', () => {
    editor.chain().focus().toggleUnderline().run()
    underlineBtnActivated()
  })


  fontSizeInputBox.addEventListener('keyup', (event) => {
    if (event.key.toLowerCase() === 'enter') {
      editor.commands.setFontSize(`${fontSizeInputBox.value}px`)
    }
  })


  selectedFont.addEventListener('click', toggleHideShowSelection)


  // Update the font size input box value, when the user uses the mouse cursor to select texts on the page
  docPage.addEventListener('mouseup', (event) => {
    let selectedText = event.target
    fontSize = selectedText.style.getPropertyValue('font-size')
    updateFontSize()
    updateFontStyle()
  })


  docPage.addEventListener('keyup', (event) => {
    let clickedKey = event.key
    if (navKeys.includes(clickedKey)) {
      let selectedElement = getElementAtCursor()
      fontSize = selectedElement.style.getPropertyValue('font-size')
      updateFontSize()
      updateFontStyle()
    }
  })

  workspace.addEventListener('click', () => {
    selections.classList.add('hidden')
  })
}

editor()

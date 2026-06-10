import { Editor } from 'https://esm.sh/@tiptap/core'
import StarterKit from 'https://esm.sh/@tiptap/starter-kit'
import { Focus, Selection } from 'https://esm.sh/@tiptap/extensions'
import { FontSize, TextStyle, FontFamily } from 'https://esm.sh/@tiptap/extension-text-style'
import { Markdown } from 'https://esm.sh/@tiptap/markdown'
import Heading from 'https://esm.sh/@tiptap/extension-heading'
import TextAlign from 'https://esm.sh/@tiptap/extension-text-align'


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
  const fontSelections = document.getElementById('font-selections')
  const selectedFont = document.getElementById('selected-font')
  const selectedStyle = document.getElementById('selected-font-style')
  const styleSelections = document.getElementById('style-selections')
  const alignLeft = document.getElementById('align-left')
  const alignCenter = document.getElementById('align-center')
  const alignRight = document.getElementById('align-right')
  const alignJustify = document.getElementById('align-justify')


  let fontSize = 16
  const navKeys = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown']
  let font
  let isFontSelectionHide = true
  let isStyleSelectionHide = true
  let headingStyle
  const alignButtons = [alignLeft, alignCenter, alignRight, alignJustify];


  let editor = new Editor({
    element: workspace,
    extensions: [
      StarterKit,
      FontSize,
      TextStyle,
      FontFamily,
      Markdown,
      Heading.configure({
        levels: [1, 2, 3, 4, 5, 6],
      }),
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
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


  const alignLeftActivated = () => {
    if (editor.isActive({ textAlign: 'left' })) {
      alignLeft.classList.add('active')
    } else {
      alignLeft.classList.remove('active')
    }
  }


  const alignRightActivated = () => {
    if (editor.isActive({ textAlign: 'right' })) {
      alignRight.classList.add('active')
    } else {
      alignRight.classList.remove('active')
    }
  }


  const alignCenterActivated = () => {
    if (editor.isActive({ textAlign: 'center' })) {
      alignCenter.classList.add('active')
    } else {
      alignCenter.classList.remove('active')
    }
  }


  const alignJustifyActivated = () => {
    if (editor.isActive({ textAlign: 'justify' })) {
      alignJustify.classList.add('active')
    } else {
      alignJustify.classList.remove('active')
    }
  }


  // This helps to update immediately when the user changes the align of the text
  // I can use this same function for every single align button
  const alignButtonsUpdate = () => {
    alignCenterActivated()
    alignJustifyActivated()
    alignLeftActivated()
    alignRightActivated()
  }


  const updateFontSize = () => {
    if (fontSize == '') return // If user clicks somewhere except the text, there would be no font size, so if it is true, it will return and stop the rest of the function
    fontSizeInputBox.value = parseFloat(fontSize) // Convert the px value to an int
  }


  const updateHeadingType = () => {
    if (editor.isActive('heading', { level: 1 })) {
      selectedStyle.querySelector('span').innerText = 'H1'
    } else if (editor.isActive('heading', { level: 2 })) {
      selectedStyle.querySelector('span').innerText = 'H2'
    } else if (editor.isActive('heading', { level: 3 })) {
      selectedStyle.querySelector('span').innerText = 'H3'
    } else if (editor.isActive('heading', { level: 4 })) {
      selectedStyle.querySelector('span').innerText = 'H4'
    } else if (editor.isActive('heading', { level: 5 })) {
      selectedStyle.querySelector('span').innerText = 'H5'
    } else if (editor.isActive('heading', { level: 6 })) {
      selectedStyle.querySelector('span').innerText = 'H6'
    } else {
      selectedStyle.querySelector('span').innerText = 'P'
    }
  }


  const updateFontStyle = () => {
    boldbtnActivated();
    underlineBtnActivated();
    italicbtnActivated();
    updateHeadingType();
  }


  const getElementAtCursor = () => {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
      let node = selection.anchorNode
      return node.nodeType === 3 ? node.parentNode : node;
    }
    return null;
  }


  const toggleHideShowFontSelection = () => {
    if (isFontSelectionHide) {
      fontSelections.classList.remove('hidden')
      isFontSelectionHide = false
    } else {
      fontSelections.classList.add('hidden')
      isFontSelectionHide = true
    }
  }


  const toggleHideShowStyleSelection = () => {
    if (isStyleSelectionHide) {
      styleSelections.classList.remove('hidden')
      isStyleSelectionHide = false
    } else {
      styleSelections.classList.add('hidden')
      isStyleSelectionHide = true
    }
  }


  const hideSelection = () => {
    fontSelections.classList.add('hidden')
    isFontSelectionHide = true
    styleSelections.classList.add('hidden')
    isStyleSelectionHide = true
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


  fontSelections.addEventListener('click', (event) => {
    let clickedFontFamily = event.target
    if (clickedFontFamily.tagName.toLowerCase() != 'span') return
    font = clickedFontFamily.dataset.value;
    editor.chain().focus().setFontFamily(font).run()
    selectedFont.querySelector('span').innerText = event.target.innerText
    toggleHideShowFontSelection()
  })


  styleSelections.addEventListener('click', (event) => {
    let clickedFontStyle = event.target
    if (clickedFontStyle.tagName.toLowerCase() != 'span') return
    headingStyle = clickedFontStyle.dataset.value
    editor.chain().focus().toggleHeading({ level: Number(headingStyle) }).run()
    toggleHideShowStyleSelection()
    updateHeadingType()
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


  alignJustify.addEventListener('click', () => {
    editor.chain().focus().toggleTextAlign('justify').run()
    alignJustifyActivated()
  })


  alignLeft.addEventListener('click', () => {
    editor.chain().focus().toggleTextAlign('left').run()
    alignLeftActivated()
  })


  alignRight.addEventListener('click', () => {
    editor.chain().focus().toggleTextAlign('right').run()
    alignRightActivated()
  })


  alignCenter.addEventListener('click', () => {
    editor.chain().focus().toggleTextAlign('center').run()
    alignCenterActivated()
  })


  alignJustify.addEventListener('click', () => {
    editor.chain().focus().toggleTextAlign('justify').run()
    alignButtonsUpdate()
  })


  alignButtons.forEach((element) => {
    element.addEventListener('click', alignButtonsUpdate)
  });


  fontSizeInputBox.addEventListener('keyup', (event) => {
    if (event.key.toLowerCase() === 'enter') {
      editor.commands.setFontSize(`${fontSizeInputBox.value}px`)
    }
  })


  selectedFont.addEventListener('click', toggleHideShowFontSelection)
  selectedStyle.addEventListener('click', toggleHideShowStyleSelection)


  // Update the font size input box value, when the user uses the mouse cursor to select texts on the page
  docPage.addEventListener('mouseup', (event) => {
    let selectedText = event.target
    fontSize = selectedText.style.getPropertyValue('font-size')
    updateFontSize()
    updateFontStyle()
    updateHeadingType()
    alignButtonsUpdate()
  })


  docPage.addEventListener('keyup', (event) => {
    updateHeadingType() // Heading type should be updated with typing although it is in the updateFontStyle
    alignButtonsUpdate()
    let clickedKey = event.key
    // used an if statement, to reduce the process of the program
    if (navKeys.includes(clickedKey)) {
      let selectedElement = getElementAtCursor()
      fontSize = selectedElement.style.getPropertyValue('font-size')
      updateFontSize()
      updateFontStyle()
    }
  })


  workspace.addEventListener('click', () => {
    hideSelection()
  })
}

editor()

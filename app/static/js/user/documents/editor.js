import { Editor } from 'https://esm.sh/@tiptap/core'
import StarterKit from 'https://esm.sh/@tiptap/starter-kit'
import { FontSize, TextStyle } from 'https://esm.sh/@tiptap/extension-text-style'
import { Focus, Selection } from 'https://esm.sh/@tiptap/extensions'
// import Bold from 'https://esm.sh/@tiptap/extension-bold'
import Underline from 'https://esm.sh/@tiptap/extension-underline'


const boldBtn = document.getElementById('bold-btn')
const italicBtn = document.getElementById('italic-btn')
const underlineBtn = document.getElementById('underline-btn')
const fontSizeInputBox = document.getElementById('font-size')
const workspace = document.getElementById('workspace')


let isBold = false
let isItalic = false
let isUnderline = false
const navKeys = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown']
let fontSize = 16

let editor = null;

function initEditor(root = document) {
  const el = root.querySelector('#workspace');

  if (!el) return;

  // prevent duplicate init
  if (el.dataset.initialized) return;
  el.dataset.initialized = "true";

  // optional: clean up old editor
  if (editor) {
    editor.destroy();
    editor = null;
  }

  editor = new Editor({
    element: el,
    extensions: [
      StarterKit,
      Underline,
      TextStyle,
      FontSize,
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
  });

  const boldFunction = () => {
    if (!isBold) {
      isBold = true
      boldBtn.children[0].style.backgroundColor = '#0E1116';
    } else {
      isBold = false
      boldBtn.children[0].style.backgroundColor = 'rgba(14, 17, 22, 0.5)';
    }
  }

  boldBtn.addEventListener('click', () => {
    boldFunction();
    editor.chain().focus().toggleBold().run();
  })

}

// run on first load
initEditor();

editor.commands.setFontSize('16px')


const docPage = document.querySelector('.tiptap')





const italicFunction = () => {
  editor.chain().focus().toggleItalic().run()
  if (!isItalic) {
    isItalic = true
    italicBtn.children[0].style.backgroundColor = '#0E1116';
  } else {
    isItalic = false
    italicBtn.children[0].style.backgroundColor = 'rgba(14, 17, 22, 0.5)';
  }
}


const underlineFunction = () => {
  editor.chain().focus().toggleUnderline().run()
  if (!isUnderline) {
    isUnderline = true
    underlineBtn.children[0].style.backgroundColor = '#0E1116';
  } else {
    isUnderline = false
    underlineBtn.children[0].style.backgroundColor = 'rgba(14, 17, 22, 0.5)';
  }
}


const updateFontSize = () => {
  if (fontSize == '') return // If user clicks somewhere except the text, there would be no font size, so if it is true, it will return and stop the rest of the function
  fontSizeInputBox.value = parseFloat(fontSize) // Convert the px value to an int
}


const getElementAtCursor = () => {
  const selection = window.getSelection();
  if (selection.rangeCount > 0) {
    let node = selection.anchorNode
    return node.nodeType === 3 ? node.parentNode : node;
  }
  return null;
}


// const updateFontStyle = (clickedElement) => {
//   let selectedElementTagName = clickedElement.tagName;
//   while (selectedElementTagName != 'SPAN') {
//     console.log(selectedElementTagName)
//     clickedElement = clickedElement.parentElement;
//     selectedElementTagName = clickedElement.tagName
//   }
// }


const updateFontStyle = () => {
  if (editor.isActive('bold')) {
    boldBtn.children[0].style.backgroundColor = '#0E1116';
  } else {
    boldBtn.children[0].style.backgroundColor = 'rgba(14, 17, 22, 0.5)';
  }

  if (editor.isActive('underline')) {
    underlineBtn.children[0].style.backgroundColor = '#0E1116';
  } else {
    underlineBtn.children[0].style.backgroundColor = 'rgba(14, 17, 22, 0.5)';
  }
}




italicBtn.addEventListener('click', italicFunction)
underlineBtn.addEventListener('click', underlineFunction)


// Short Cut keys for the tool bar
document.addEventListener('keydown', (event) => {
  if (event.ctrlKey) {
    if (event.key.toLowerCase() === 'b') {
      event.preventDefault();
      boldFunction();
    } else if (event.key.toLowerCase() === 'i') {
      event.preventDefault()
      italicFunction()
    } else if (event.key.toLowerCase() === 'u') {
      event.preventDefault();
      underlineFunction();
    }
  }
})


fontSizeInputBox.addEventListener('keyup', (event) => {
  if (event.key.toLowerCase() === 'enter') {
    editor.commands.setFontSize(`${fontSizeInputBox.value}px`)
  }
})


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

// TODO: Italic, and undelrin dont work like bold
//
document.body.addEventListener('htmx:load', (e) => {
  initEditor(e.target);
});

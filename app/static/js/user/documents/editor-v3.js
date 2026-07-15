(() => {
  function extractDocumentParts(html) {
      let parser = new DOMParser();
      let documentObject = parser.parseFromString(html, "text/html");

      return {
          bodyHtml: documentObject.body.innerHTML,
          css: Array.from(documentObject.querySelectorAll("style"))
              .map(function(style) {
                  return style.textContent;
              })
              .join("\n")
      };

  }

  let cvDocument = extractDocumentParts(doc);

  tinymce.init({
      selector: "#editor",
      inline: false,
      height: 900,
      menubar: true,
      resize: true,

      plugins: [
              "lists",
              "link",
              "table",
              "searchreplace",
              "code",
              "fullscreen",
              "wordcount"
      ],

      toolbar:
              "undo redo | " +
              "blocks fontfamily fontsize | " +
              "bold italic underline forecolor | " +
              "alignleft aligncenter alignright alignjustify | " +
              "bullist numlist outdent indent | " +
              "link table | " +
              "removeformat | " +
              "searchreplace | " +
              "code fullscreen",

      content_style:
          cvDocument.css +
          `
          body {
              width: 210mm;
              min-height: 297mm;
              margin: 0 auto;
              padding: 16mm 18mm;
              box-sizing: border-box;
              background: white;
          }
          `,

      setup: function(editor) {
          editor.on("init", function() {
              editor.setContent(cvDocument.bodyHtml);
          });
      }
  });

  document.getElementById("save").addEventListener("click", function() {

      let editor = tinymce.get("editor");

      if (!editor) {
          console.error("Editor is not initialized.");
          return;
      }

      let finalHtml =
        `<!DOCTYPE html>
        <html lang="en">
          <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <style>
              ${cvDocument.css}
            </style>
          </head>

          <body>
            ${editor.getContent()}
          </body>

        </html>`;

      console.log(finalHtml);

      // Send finalHtml to Flask
  });
})();

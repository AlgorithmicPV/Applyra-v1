const serverResponseHandler = (evt) => {
  response = evt.detail.xhr

  let contentType = response.getResponseHeader('Content-Type')

  /* Prevent from swapping HTML if the content type is json, 
   * because, its because server detects an error */
  if (contentType == 'application/json') {
    evt.preventDefault();
  }
}

/* Why am I removing the EventListener ? */
/* Because I am using HTMX, so the page doesn't reload, so the browser saves the EventListener temp,
 * and, when I go back and come again, it duplicates, so to stop that, before run this, remove the
 * exisiting EventListener */
document.body.removeEventListener("htmx:beforeSwap", serverResponseHandler);
document.body.addEventListener("htmx:beforeSwap", serverResponseHandler)


/* Remember the csrf_toke, this will expire, so remember to make it as a seperate rror for that */

const handler = (evt) => {

  response = evt.detail.xhr
  message = JSON.parse(response['response'])
  console.log(message)
}


/* Why am I removing the EventListener ? */
/* Because I am using HTMX, so the page doesn't reload, so the browser saves the EventListener temp,
 * and, when I go back and come again, it duplicates, so to stop that, before run this, remove the
 * exisiting EventListener */
document.body.removeEventListener("htmx:beforeSwap", handler);
document.body.addEventListener("htmx:beforeSwap", handler)


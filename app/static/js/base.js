const serverResponseHandler = (evt) => {
  response = evt.detail.xhr;

  let contentType = response.getResponseHeader("Content-Type");

  /* Prevent from swapping HTML if the content type is json,
   * because, its because server detects an error */
  if (contentType == "application/json") {
    evt.preventDefault();
  }
};

/* Why am I removing the EventListener ? */
/* Because I am using HTMX, so the page doesn't reload, so the browser saves the EventListener temp,
 * and, when I go back and come again, it duplicates, so to stop that, before run this, remove the
 * exisiting EventListener */
document.body.removeEventListener("htmx:beforeSwap", serverResponseHandler);
document.body.addEventListener("htmx:beforeSwap", serverResponseHandler);

/* Remember the csrf_toke, this will expire, so remember to make it as a seperate rror for that */

const notificationBox = (className, message) => {
  const page = document.getElementById("page");
  const wrapper = document.createElement("div");
  wrapper.classList.add(className);

  const messageText = document.createElement("p");
  messageText.innerText = message;

  const closeButton = document.createElement("button");
  closeButton.classList.add("close-btn");
  closeButton.innerHTML = "&#x292B;";

  wrapper.appendChild(messageText);
  wrapper.appendChild(closeButton);

  page.appendChild(wrapper);

  // trigger animation after adding to DOM
  requestAnimationFrame(() => {
    wrapper.classList.add("show");
  });

  closeButton.addEventListener("click", () => {
    wrapper.classList.remove("show");
    wrapper.classList.add("hide");

    setTimeout(() => {
      wrapper.remove();
    }, 350);
  });
};

const handler = (evt) => {
  let response = evt.detail.xhr;
  let contentType = response.getResponseHeader("Content-Type");

  if (contentType != "application/json") return;

  let message = JSON.parse(response["response"]);
  let key = Object.keys(message)[0];
  let value = Object.values(message).flat()[0];

  if (key == "error") {
    notificationBox("error-notification", value);
  } else if (key == "success") {
    notificationBox("success-notification", value);
  } else {
    notificationBox("warning-notification", value);
  }
};

/* Why am I removing the EventListener ? */
/* Because I am using HTMX, so the page doesn't reload, so the browser saves the EventListener temp,
 * and, when I go back and come again, it duplicates, so to stop that, before run this, remove the
 * exisiting EventListener */
document.body.removeEventListener("htmx:beforeSwap", handler);
document.body.addEventListener("htmx:beforeSwap", handler);

const selectNavButton = (selectedButton) => {
  document.querySelectorAll(".nav-page-btn").forEach((button) => {
    const isSelected = button === selectedButton;
    button.classList.toggle("active", isSelected);

    if (isSelected) {
      button.setAttribute("aria-current", "page");
    } else {
      button.removeAttribute("aria-current");
    }
  });
};

const initialNavButton = document.querySelector(".nav-page-btn.active");
if (initialNavButton) selectNavButton(initialNavButton);

document.addEventListener("click", (event) => {
  const navButton = event.target.closest(".nav-page-btn");
  if (navButton) selectNavButton(navButton);
});

window.addEventListener("popstate", () => {
  const navButton = Array.from(document.querySelectorAll(".nav-page-btn")).find(
    (button) => window.location.pathname.startsWith(button.dataset.navPath),
  );

  if (navButton) selectNavButton(navButton);
});

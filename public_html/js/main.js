window.onload = function () {
  /************************
   * Simple MCQ handling
   ***********************/
  // Whenever someone clicks on a radio button in the mcq_correct class, add the correct answer
  document.querySelectorAll('.mcq_correct input').forEach(function (el) {
    el.addEventListener('click', function (e) {
      let correct_box = document.createElement('span');
      correct_box.setAttribute('aria-live', 'assertive');
      if (el.parentElement.querySelector('span') == null)
        el.parentElement.appendChild(correct_box);
      correct_box.textContent = ' Correct!';
    });
  });

  // Make the table of contents.
  // Don't add it to any page with the class "no_toc"
  if (!document.querySelector('body').classList.contains('no_toc')) {
    makeTOC();
  }
};

/**
 * This function creates a table of contents for the page.
 * It is called by the window.onload function above.
 *
 * @param {void}
 * @returns {void}
 */
function makeTOC() {
  // Make the container for the table of contents.
  // It gets added as the first child of the <main> element.

  let toc = document.createElement('div');
  toc.id = 'toc';
  let main = document.querySelector('main');
  main.insertBefore(toc, main.firstChild);

  // Add a skip to main content link
  let skip_link = document.createElement('a');
  skip_link.href = '#main_content';
  skip_link.classList.add('sr-only');
  skip_link.textContent = 'Skip to main content';
  toc.appendChild(skip_link);

  // Add a checkbox to control the table of contents
  let menu_control = document.createElement('input');
  menu_control.id = 'menu_control';
  menu_control.type = 'checkbox';
  toc.appendChild(menu_control);

  // Add a label for the checkbox
  let menu_label = document.createElement('label');
  menu_label.setAttribute('for', 'menu_control');
  menu_label.classList.add('menu_control');
  toc.appendChild(menu_label);

  // Add a span for the open menu button
  let open_menu = document.createElement('span');
  open_menu.classList.add('open-toc');
  open_menu.setAttribute('aria-label', 'Open Table of Contents');
  open_menu.textContent = ' ≡';
  menu_label.appendChild(open_menu);

  // Add a span for the close menu button
  let close_menu = document.createElement('span');
  close_menu.classList.add('close-toc');
  close_menu.setAttribute('aria-label', 'Close Table of Contents');
  close_menu.textContent = ' ╳';
  menu_label.appendChild(close_menu);

  // Give the TOC a box to hold the header
  let toc_header_box = document.createElement('div');
  toc_header_box.id = 'toc_header_box';

  // Add a title for the table of contents
  let toc_title = document.createElement('h1');
  toc_title.textContent = 'Table of Contents';
  toc.appendChild(toc_header_box);
  toc_header_box.appendChild(toc_title);

  // Add a container for the table of contents
  let toc_menu = document.createElement('div');
  toc_menu.id = 'toc_menu';
  toc.appendChild(toc_menu);

  // This section creates a table of contents from
  // most of the headings on the page. We skip
  // headings inside the <details> element.
  let toc_list = document.createElement('ul');
  toc_menu.appendChild(toc_list);
  let headings = document.querySelectorAll(
    'h2:not(details h2), h3:not(details h3), h4:not(details h4), h5:not(details h5), h6:not(details h6)'
  );

  // Assign IDs to each heading on the page
  for (let i = 0; i < headings.length; i++) {
    let heading = headings[i];
    heading.id = 'heading-' + i;
  }
  // Create a list element for each heading
  for (let i = 0; i < headings.length; i++) {
    let heading = headings[i];
    let li = document.createElement('li');
    let a = document.createElement('a');
    a.href = '#' + heading.id;
    a.textContent = heading.textContent;

    // Add a class based on the heading's level
    let level = heading.tagName[1];
    li.classList.add('toc_link_h' + level);

    li.appendChild(a);
    toc_list.appendChild(li);
  }
}

const loadSettingsTomSelect = () => {
  document.querySelectorAll(".settings-skill-select").forEach((select) => {
    if (select.tomselect) return;

    new TomSelect(select, {
      valueField: "id",
      labelField: "name",
      searchField: "name",
      maxItems: 1,
      load: function (query, callback) {
        fetch(select.dataset.searchUrl + "?q=" + encodeURIComponent(query))
          .then((response) => response.json())
          .then((data) => callback(data))
          .catch(() => callback());
      },
    });
  });

  document.querySelectorAll(".settings-job-type").forEach((select) => {
    if (select.tomselect) return;

    const jobTypes = [];

    select.querySelectorAll("option").forEach((option) => {
      jobTypes.push({
        value: option.value,
        text: option.text,
      });
    });

    new TomSelect(select, {
      options: jobTypes,
      items: select.value ? [select.value] : [],
      maxItems: 1,
      create: false,
      valueField: "value",
      labelField: "text",
      searchField: "text",
    });
  });
};

const openSettingsForm = (button) => {
  button.closest(".settings-popup").classList.add("open");
};

const closeSettingsForm = (button) => {
  button.closest(".settings-popup").classList.remove("open");
};

document.body.addEventListener("htmx:load", loadSettingsTomSelect);
loadSettingsTomSelect();

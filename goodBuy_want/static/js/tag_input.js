document.addEventListener("DOMContentLoaded", function () {
  const tagInput = document.getElementById("tag-input");
  // 要使用Djano Forms tag name 前面要加id
  const tagHidden = document.getElementById("id_tag_names");
  const tagList = document.getElementById("tag-area");
  const suggestionBox = document.getElementById("tag-suggestions");
  const tagSet = new Set();

  // 初始化：載入既有 tag
  document.querySelectorAll("#tag-area .tag-badge").forEach(el => {
    tagSet.add(el.getAttribute("data-tag"));
  });
  tagHidden.value = [...tagSet].join(",");

  //==============
  // 渲染標籤列
  function renderTags() {
    tagList.innerHTML = "";
    tagSet.forEach(tag => {
      const span = document.createElement("span");
      span.className = "badge bg-light text-dark tag-badge me-1";
      span.setAttribute("data-tag", tag);
      span.innerHTML = `<img src="/static/img/x.png" alt="刪除" style="cursor:pointer; width:16px; height:16px;" class="ms-1 remove-tag"> ${tag} `;
      span.querySelector(".remove-tag").addEventListener("click", () => {
        tagSet.delete(tag);
        renderTags();
      });
      tagList.appendChild(span);
    });
    // 更新 隱藏input
    tagHidden.value = [...tagSet].join(",");
  }

  // 顯示初始標籤
  document.querySelectorAll("#tag-area .tag-badge").forEach(el => {
  tagSet.add(el.getAttribute("data-tag"));
  });
  tagHidden.value = [...tagSet].join(",");
  renderTags();
  //==============

  tagInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      const val = this.value.trim();
      if (val && !tagSet.has(val)) {
        tagSet.add(val);
        renderTags();
      }
      this.value = "";
      suggestionBox.innerHTML = "";
    }
  });

  document.querySelectorAll(".tag-option").forEach(btn => {
    btn.addEventListener("click", () => {
      const val = btn.textContent.trim();
      if (!tagSet.has(val)) {
        tagSet.add(val);
        renderTags();
      }
    });
  });

  // 搜尋建議
  tagInput.addEventListener("input", function () {
    const query = this.value.trim();
    if (!query) {
      suggestionBox.innerHTML = "";
      return;
    }

    fetch(`/tag/api/search?q=${encodeURIComponent(query)}`)
      .then(res => res.json())
      .then(data => {
        suggestionBox.innerHTML = "";
        data.forEach(item => {
          const li = document.createElement("li");
          li.className = "list-group-item list-group-item-action";
          li.textContent = item.name;
          li.addEventListener("click", () => {
            if (!tagSet.has(item.name)) {
              tagSet.add(item.name);
              renderTags();
            }
            tagInput.value = "";
            suggestionBox.innerHTML = "";
          });
          suggestionBox.appendChild(li);
        });
      });
  });
});

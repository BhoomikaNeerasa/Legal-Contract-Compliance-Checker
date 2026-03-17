// Make sure DOM is ready
window.addEventListener("load", function () {

  const helpBtn = document.getElementById("helpBtn");
  const helpOverlay = document.getElementById("helpOverlay");
  const helpContent = document.getElementById("helpContent");
  const helpTitle = document.getElementById("helpTitle");
  const helpBack = document.getElementById("helpBack");
  const helpClose = document.getElementById("helpClose");

  if (!helpBtn) {
    console.error("Help button not found");
    return;
  }

  let currentView = "categories";
  let selectedCategory = null;

  helpBtn.onclick = function () {
    helpOverlay.classList.remove("d-none");
    showCategories();
  };

  helpClose.onclick = function () {
    helpOverlay.classList.add("d-none");
  };

  helpBack.onclick = function () {
    if (currentView === "questions") {
      showCategories();
    } else if (currentView === "answer") {
      showQuestions(selectedCategory);
    }
  };

  function showCategories() {
    currentView = "categories";
    helpTitle.textContent = "Help Center";
    helpBack.classList.add("d-none");
    helpContent.innerHTML = "";

    HELP_DATA.forEach(cat => {
      helpContent.innerHTML += `
        <div class="help-item" data-category="${cat.category}">
          ${cat.category}
        </div>`;
    });

    document.querySelectorAll(".help-item").forEach(item => {
      item.onclick = function () {
        showQuestions(this.dataset.category);
      };
    });
  }

  function showQuestions(categoryName) {
    currentView = "questions";
    selectedCategory = categoryName;
    helpTitle.textContent = categoryName;
    helpBack.classList.remove("d-none");
    helpContent.innerHTML = "";

    const category = HELP_DATA.find(c => c.category === categoryName);

    category.questions.forEach(q => {
      helpContent.innerHTML += `
        <div class="help-item" data-question="${q.question}">
          ${q.question}
        </div>`;
    });

    document.querySelectorAll(".help-item").forEach(item => {
      item.onclick = function () {
        showAnswer(categoryName, this.dataset.question);
      };
    });
  }

  function showAnswer(categoryName, questionText) {
    currentView = "answer";
    helpBack.classList.remove("d-none");

    const category = HELP_DATA.find(c => c.category === categoryName);
    const question = category.questions.find(q => q.question === questionText);

    helpTitle.textContent = questionText;

    helpContent.innerHTML = `
      <p>${question.answer}</p>
      <hr>
      <div class="text-center mt-3">
        <button class="btn btn-primary" id="askChatbotBtn">
          Still need help? Ask chatbot
        </button>
      </div>
    `;

    document.getElementById("askChatbotBtn").onclick = function () {

  const chatSection = document.getElementById("chatSection");
  const chatInput = document.getElementById("chatInput");

  // If chatbot does not exist OR contract not analyzed
  if (!chatSection || chatSection.classList.contains("d-none")) {

    if (!document.getElementById("contractAlert")) {

      const alertBox = document.createElement("div");
      alertBox.id = "contractAlert";
      alertBox.className = "alert alert-warning mt-3";
      alertBox.innerHTML =
        "To use the AI Legal Assistant, please upload and analyze a contract first.";

      helpContent.appendChild(alertBox);
    }

  } else {

    helpOverlay.classList.add("d-none");

    chatSection.scrollIntoView({ behavior: "smooth" });

    setTimeout(() => {
      chatInput.focus();
    }, 500);
  }
};
}

});
// test 彈跳式頁面(第一次寫)
document.addEventListener("DOMContentLoaded", function () {
    const openModalBtn = document.getElementById("open-modal");
    const modalOverlay = document.getElementById("modal-overlay");
    const modalContent = document.getElementById("modal-content");

    if (openModalBtn) {
        openModalBtn.addEventListener("click", function () {
            fetch("login.html")  // 載入 login.html
                .then(response => response.text())
                .then(data => {
                    modalContent.innerHTML = data;
                    modalOverlay.style.display = "block";

                    // 綁定關閉按鈕
                    const closeModalBtn = document.getElementById("close-modal");
                    if (closeModalBtn) {
                        closeModalBtn.addEventListener("click", function () {
                            modalOverlay.style.display = "none";
                        });
                    }
                });
        });
    }
});
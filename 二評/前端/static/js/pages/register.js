document.addEventListener("DOMContentLoaded", () => {
  const termsBox = document.getElementById("termsBox");
  const agreeCheckbox = document.getElementById("agreeCheckbox");
  const submitBtn = document.getElementById("submitBtn");

  // 條款滑到底才開放勾選
  termsBox.addEventListener("scroll", () => {
    const { scrollTop, scrollHeight, clientHeight } = termsBox;
    if (scrollTop + clientHeight >= scrollHeight - 5) {
      agreeCheckbox.disabled = false;
    }
  });

  // 勾選後啟用送出按鈕
  agreeCheckbox.addEventListener("change", () => {
    submitBtn.disabled = !agreeCheckbox.checked;
  });

  // 聚焦動畫
  const fields = document.querySelectorAll("input, select");
  fields.forEach(field => {
    field.addEventListener("focus", () => {
      field.style.boxShadow = "0 0 10px #26F8FF";
    });
    field.addEventListener("blur", () => {
      field.style.boxShadow = "none";
    });
  });
});
document.addEventListener("DOMContentLoaded", () => {
  const photoInput = document.getElementById("photo");
  const photoPreview = document.getElementById("photoPreview");
  const photoBox = document.querySelector(".photo-upload");

  photoInput.addEventListener("change", () => {
    const file = photoInput.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = e => {
        photoPreview.src = e.target.result;
        photoPreview.style.display = "block";
        photoBox.classList.add("has-image");
      };
      reader.readAsDataURL(file);
    }
  });
});

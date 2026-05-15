document.addEventListener("DOMContentLoaded", () => {
  const botaoSobreCalculo = document.querySelector(".botao-info");
  const secaoSobreCalculo = document.querySelector("#sobre-calculo");

  if (botaoSobreCalculo && secaoSobreCalculo) {
    botaoSobreCalculo.addEventListener("click", (event) => {
      event.preventDefault();

      secaoSobreCalculo.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });
    });
  }

  const trilha = document.querySelector(".carrossel-trilha");
  const slides = document.querySelectorAll(".slide-sobre");
  const botaoAnterior = document.querySelector(".seta-esquerda");
  const botaoProximo = document.querySelector(".seta-direita");
  const indicadoresContainer = document.querySelector(".indicadores-carrossel");

  if (!trilha || !slides.length || !botaoAnterior || !botaoProximo || !indicadoresContainer) {
    return;
  }

  let indiceAtual = 0;
  let totalPosicoes = 0;

  function obterQuantidadeVisivel() {
    const larguraTela = window.innerWidth;

    if (larguraTela <= 800) {
      return 1;
    }

    if (larguraTela <= 1200) {
      return 2;
    }

    return 3;
  }

  function obterDistanciaSlide() {
    const primeiroSlide = slides[0];
    const estilosTrilha = window.getComputedStyle(trilha);
    const gap = parseFloat(estilosTrilha.gap) || 0;
    const larguraSlide = primeiroSlide.getBoundingClientRect().width;

    return larguraSlide + gap;
  }

  function criarIndicadores() {
    indicadoresContainer.innerHTML = "";

    for (let i = 0; i < totalPosicoes; i++) {
      const indicador = document.createElement("button");
      indicador.classList.add("indicador");
      indicador.type = "button";
      indicador.setAttribute("aria-label", `Ir para a posição ${i + 1}`);

      indicador.addEventListener("click", () => {
        indiceAtual = i;
        atualizarCarrossel();
      });

      indicadoresContainer.appendChild(indicador);
    }
  }

  function atualizarCarrossel() {
    const distancia = obterDistanciaSlide();
    trilha.style.transform = `translateX(-${indiceAtual * distancia}px)`;

    const indicadores = document.querySelectorAll(".indicador");

    indicadores.forEach((indicador, index) => {
      indicador.classList.toggle("ativo", index === indiceAtual);
    });

    botaoAnterior.disabled = indiceAtual === 0;
    botaoProximo.disabled = indiceAtual >= totalPosicoes - 1;
  }

  function configurarCarrossel() {
    const quantidadeVisivel = obterQuantidadeVisivel();

    totalPosicoes = Math.max(slides.length - quantidadeVisivel + 1, 1);

    if (indiceAtual > totalPosicoes - 1) {
      indiceAtual = totalPosicoes - 1;
    }

    criarIndicadores();
    atualizarCarrossel();

    const mostrarControles = totalPosicoes > 1;

    botaoAnterior.style.display = mostrarControles ? "flex" : "none";
    botaoProximo.style.display = mostrarControles ? "flex" : "none";
    indicadoresContainer.style.display = mostrarControles ? "flex" : "none";
  }

  botaoAnterior.addEventListener("click", () => {
    if (indiceAtual > 0) {
      indiceAtual--;
      atualizarCarrossel();
    }
  });

  botaoProximo.addEventListener("click", () => {
    if (indiceAtual < totalPosicoes - 1) {
      indiceAtual++;
      atualizarCarrossel();
    }
  });

  let temporizadorResize;

  window.addEventListener("resize", () => {
    clearTimeout(temporizadorResize);

    temporizadorResize = setTimeout(() => {
      configurarCarrossel();
    }, 150);
  });

  configurarCarrossel();
});
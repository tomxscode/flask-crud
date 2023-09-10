function graficoPastel(labels, valores, colores, elementoHtml) {
    let elemento = document.getElementById(elementoHtml);
    let ctx = elemento.getContext('2d');
    let myChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: valores,
                backgroundColor: colores
            }]
        },
    });
}
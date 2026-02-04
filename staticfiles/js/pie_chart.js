var data = {
    labels: ["Terminada", "No Terminada"],
    datasets: [{
        data: [done_tasks, not_done_tasks],
        backgroundColor: ["green", "red"]
    }]
};

let done_porcentaje = document.getElementById("done_porcentaje").getContext("2d");
let done_porcentajeChart = new Chart(done_porcentaje, {
    type: "pie",
    data: data,
    options: {
        plugins: {
            title: {
                display: true,
                text: "Tareas Terminadas En %",
                font: {
                    size: 20
                }
            },
            legend: {
                labels: {
                    font: {
                        size: 18
                    }
                }
            }
        }
    }
});

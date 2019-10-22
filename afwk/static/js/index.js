var secuencia = null;
var reverso = false;
var word = ""
// Update the current slider value (each time you drag the slider handle)
$(document).on('input', "#myRange", function (event) {
  changeSlider();
  var j = 1;
  var k = 1;
  for (var i = 0; i < $("#myRange").val(); i++) {
    if (secuencia[i][1] == "λ") k += 1;
    else j += 1;
  }
  if (reverso) k = word.length + 1 - k;
  $(".trazatdF").remove()
  columnasFlecha = "<td class='trazatdF'></td>";
  for (var i = 0; i < word.length + 2; i++) {
    columnasFlecha += "<td class='trazatdF'>" + (i == j ? "↓" : "") + "</td>"
  }
  $("#flechaSup").append(columnasFlecha)
  columnasFlecha = "<td class='trazatdF'></td>";
  for (var i = 0; i < word.length + 2; i++) {
    columnasFlecha += "<td class='trazatdF'>" + (i == k ? "↑" : "") + "</td>"
  }
  $("#flechaInf").append(columnasFlecha)
  if ($("#myRange").val() == 0) $(".estado").text(secuencia[0][0])
  else $(".estado").text(secuencia[$("#myRange").val() - 1][3])
});

function changeSlider() {
  $("#pasosSliderMark").text($("#myRange").val());
  var porc = $("#myRange").val() / $("#myRange").attr("max")
  var m = $("#myRange").innerWidth() - 25;
  var n = 12.5 - $("#pasosSliderMark").innerWidth() / 2;

  $("#pasosSliderMark").css({ left: porc * m + n });
}


$(document).on('change', '.btn-file :file', function (event) {
  var input = $(this);
  label = input.val().replace(/\\/g, '/').replace(/.*\//, '');

  if(label.endsWith(".txt")){
    const reader = new FileReader()
    reader.onload = function (fileLoadedEvent) {
      var text = fileLoadedEvent.target.result;
      $.ajax({
        url: 'ajax/classify/',
        data: {
          'text': text
        },
        error: function(){
          update({"error": "Bad formed WKFA"});
        },
        success: function (data) {
          update(data);
        }
      });
    };
    reader.readAsText(input.get(0).files[0])
  }
  else{
    update({"error": "WKFA must be specified in a .txt file"});
  }

  var input = $(this).parents('.input-group').find(':text'),
    log = label;

  if (input.length) {
    input.val(log);
  } else {
    if (log) alert(log);
  }
  document.getElementById("fileinput").value = "";
});

$(document).on('keyup', '#word', function (event) {
  word = $("#word").val()
  $.ajax({
    url: 'ajax/analizar/',
    data: {
      'word': word
    },
    success: function (data) {
      $(".paso").remove()
      $(".trellisrow").remove()
      $(".trazatd").remove()
      $(".trazatdF").remove()
      $("#aceptada").text("The WKFA " + (data.acepta ? "does" : "doesn't") + " accept the word '" + (word.length > 0 ? word : "λ" ) + "'" + (data.probabilistico && data.acepta ? " with a max probability of " + data.probabilidad : ""));
      $("#aceptada").attr("class", data.acepta ? "text-success" : "text-danger");
      if (data.acepta) {
        for (var i = 0; i < data.secuencia.length; i++) {
          var s = data.secuencia[i];
          $("#secuencia").append("<p class='paso'>" + s[0] + ",(" + s[1] + "," + s[2] + ")->" + s[3] + "</p>");
        }
        $("#sliderTd").removeClass("hidden");
        $("#trazaAfwk").removeClass("hidden");
        $("#secuenciaTd").removeClass("hidden");
        $("#myRange").attr("max", data.secuencia.length);
        $("#myRange").val(0);
        changeSlider();
        secuencia = data.secuencia;
        reverso = data.reverso;
        columnas = ""
        columnasFlecha = "<td class='trazatdF'></td><td class='trazatdF'></td>";
        for (var i = 0; i < word.length; i++) {
          columnas += "<td class='trazatd'>" + word[i] + "</td>"
          columnasFlecha += "<td class='trazatdF'>" + (i == 0 ? "↓" : "") + "</td>"
        }
        $("#hebraSup").append(columnas)
        $("#flechaSup").append(columnasFlecha)
        columnas = ""
        columnasFlecha = "<td class='trazatdF'></td><td class='trazatdF'></td>";
        var ini = reverso ? word.length - 1 : 0;
        for (var i = 0; i < word.length; i++) {
          columnas += "<td class='trazatd'>" + data.complementaria[i] + "</td>"
          columnasFlecha += "<td class='trazatdF'>" + (i == ini ? "↑" : "") + "</td>"
        }
        $("#hebraInf").append(columnas)
        $("#flechaInf").append(columnasFlecha)
        $(".estado").text(secuencia[0][0])
      }
      else {
        if (!$("#sliderTd").hasClass("hidden"))
          $("#sliderTd").addClass("hidden");
        if (!$("#trazaAfwk").hasClass("hidden"))
          $("#trazaAfwk").addClass("hidden");
        if (!$("#secuenciaTd").hasClass("hidden"))
          $("#secuenciaTd").addClass("hidden");
      }
      $("#trellis").append("<h3 class='trellisrow'>Trellis:</h3>")
      text = "<div class='trellisrow' style='overflow-x:scroll; width:100%'><table><tbody><tr><td style='padding: 5px; text-align: center;'></td><td style='padding: 5px; text-align: center;'>$</td>"
      for(var i = 0; i < word.length; i++) {
        text += "<td style='padding: 5px; text-align: center;'>"+word[i]+"</td>"
      }
      text += "</tr>"
      for (var i = 0; i < data.trellis.length; i++) {
        text += "<tr><td style='padding: 5px; text-align: center;'>" + (i==0?"$":data.complementaria[i-1]) + "</td>"
        for (var j = 0; j < data.trellis[i].length; j++) {
          text += "<td style='padding: 5px; text-align: center;'>("
          for (var k = 0; k < data.trellis[j][i].length; k++) 
            text += (k==0 ? "" : ",") + data.trellis[j][i][k][0]
          text += ")</td>"
        }
        text += "</tr>"
      }
      $("#trellis").append(text + "</tbody></table></div>")
    }
  });
});

$(document).on('click', '#limitadoBtn', function (event) {
  $.ajax({
    url: 'ajax/convertir/',
    success: function (data) {
      update(data);
    }
  });
});

$(document).on('click', '#descargarBtn', function (event) {
  let data = 'filename=' + $("#filename").val()
  let request = new XMLHttpRequest();
  request.open('GET', 'ajax/descargar/?filename=' + $("#filename").val(), true);
  request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
  request.responseType = 'blob';

  request.onload = function (e) {
    if (this.status === 200) {
      let filename = "";
      let disposition = request.getResponseHeader('Content-Disposition');
      // check if filename is given
      if (disposition && disposition.indexOf('attachment') !== -1) {
        let filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
        let matches = filenameRegex.exec(disposition);
        if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
      }
      let blob = this.response;
      if (window.navigator.msSaveOrOpenBlob) {
        window.navigator.msSaveBlob(blob, filename);
      }
      else {
        let downloadLink = window.document.createElement('a');
        let contentTypeHeader = request.getResponseHeader("Content-Type");
        downloadLink.href = window.URL.createObjectURL(new Blob([blob], { type: contentTypeHeader }));
        downloadLink.download = filename;
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
      }
    } else {
      alert('Download failed.')
    }
  };
  request.send(data);
});

function update(data) {
  $("#word").val("")
  $("#aceptada").text("")
  $(".paso").remove()
  $(".trellisrow").remove()
  $(".trazatd").remove()
  $(".trazatdF").remove()
  if (!$("#sliderTd").hasClass("hidden"))
    $("#sliderTd").addClass("hidden");
  if (!$("#trazaAfwk").hasClass("hidden"))
    $("#trazaAfwk").addClass("hidden");
  if (!$("#secuenciaTd").hasClass("hidden"))
    $("#secuenciaTd").addClass("hidden");
  if(data.error.length > 0){
    console.log("Errorcillo: "+data.error);
    $("#tipo").text(data.error);
    $("#stateless").text("");
    $("#all_final").text("");
    $("#simple").text("");
    $("#limitado").text("");
    $("#V").text("");
    $("#compl").text("");
    $("#K").text("");
    $("#s0").text("");
    $("#F").text("");
    $("#reverso").text("");
    $("#probabilistico").text("");
    $(".transicion").remove();
    $("#limitadoBtn").addClass("hidden")
    $("#descargarBtn").addClass("hidden");
    $("#wordInput").addClass("hidden");
  }
  else{
    $("#tipo").text("The automata is ");
    $("#stateless").text((data.stateless ? " " : " non-") + "stateless, ");
    $("#stateless").attr("class", data.stateless ? "text-success" : "text-danger");
    $("#all_final").text((data.all_final ? "" : "non-") + "all-final, ");
    $("#all_final").attr("class", data.all_final ? "text-success" : "text-danger");
    $("#simple").text((data.simple ? "" : "non-") + "simple, ");
    $("#simple").attr("class", data.simple ? "text-success" : "text-danger");
    $("#limitado").text((data.limitado ? "" : "non-") + "1-limited.");
    $("#limitado").attr("class", data.limitado ? "text-success" : "text-danger");
    $("#V").text("V = " + data.V);
    $("#compl").text("γ = " + data.compl);
    $("#K").text("K = " + data.K);
    $("#s0").text("s0 = " + data.s0);
    $("#F").text("F = " + data.F);
    $("#reverso").text("The automata is " + (data.rev ? "reverse" : "normal") + ".");
    $("#probabilistico").text("The automata is " + (data.prob ? "probabilistic" : "non-probabilistic") + ".");
    $(".transicion").remove();
    $("#afwk").append(data.transiciones);
    $("#limitadoBtn").removeClass("hidden").attr("disabled", data.limitado);
    $("#descargarBtn").removeClass("hidden");
    $("#wordInput").removeClass("hidden");
    $("#word").attr("disabled", !data.limitado);
  }
}
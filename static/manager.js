$.getScript("/static/tablesorter/jquery.tablesorter.js");

$(window).ready(function() {

  // INITIALIZE - remove push and sources session info on page load
  $.get($SCRIPT_ROOT + '/reset_data');

  if( $("#usage").length == 0 ) {
    $('#login_button').val("Log in")
  }
  else {
    $('#login_button').val("Switch users")
  }

  // initially show usage

  $.get($SCRIPT_ROOT + '/usage/get', function(data){
    $('#usage_load').css('display', 'none');
    $('#usageget').html(data);
  });

  /*
    HIDE / SHOW SECTIONS
  */

  $('#usage').click(function() {
    //only get data if we're opening 
    if ($('#usageget').css('display') == 'none'){
      // loading gif
      $('#usage_load').css('display', 'block');
      $.get($SCRIPT_ROOT + '/usage/get', function(data){
        $('#usageget').html(data).slideToggle("fast");
        $('#usage_load').css('display', 'none');
        $('html,body').animate({scrollTop: $('#usage').offset().top}, 'slow');
      });
    }
    else{
      $('#usageget').slideToggle("fast");
    }
  });

  $('#account').click(function() {
    //only get data if we're opening 
    if ($('#accountget').css('display') == 'none'){
      // loading gif
      $('#account_load').css('display', 'block');
      $.get($SCRIPT_ROOT + '/account/get', function(data){
        $('#accountget').html(data).slideToggle("fast");
        $('#account_load').css('display', 'none');
        $('html,body').animate({scrollTop: $('#account').offset().top}, 'slow');
      });
    }
    else{
      $('#accountget').slideToggle("fast");
    }
  });

  $('#pylon').click(function() {
    //only get data if we're opening 
    if ($('#pylonget').css('display') == 'none'){
      // loading gif
      $('#pylon_load').css('display', 'block');
      $.get($SCRIPT_ROOT + '/pylon/get', function(data){
        $('#pylonget').html(data).slideToggle("fast");
        $('#pylon_load').css('display', 'none');
        $('html,body').animate({scrollTop: $('#pylon').offset().top}, 'slow');
      });
    }
    else{
      $('#pylonget').slideToggle("fast");
    }
  });

  $('#push').click(function() {
    //only get data if we're opening 
    if ($('#pushget').css('display') == 'none'){
      // loading gif
      $('#push_load').css('display', 'block');
      $.get($SCRIPT_ROOT + '/push/get', function(data){
        $('#pushget').html(data).slideToggle("fast");
        $('#push_load').css('display', 'none');
        $('html,body').animate({scrollTop: $('#push').offset().top}, 'slow');
      });
    }
    else{
      $('#pushget').slideToggle("fast");
    }
  });

  $('#historics').click(function() {
    if ($('#historicsget').css('display') == 'none'){
      $('#historics_load').css('display', 'block');
      $.get($SCRIPT_ROOT + '/historics/get', function(data){
        $('#historicsget').html(data).slideToggle("fast");
        $('#historics_load').css('display', 'none');
        $('html,body').animate({scrollTop: $('#historics').offset().top}, 'slow');
      });
    }
    else{
      $('#historicsget').slideToggle("fast");
    }
  });

  $('#sources').click(function() {
    //only get data if we're opening 
    if ($('#sourceget').css('display') == 'none'){
      $('#sources_load').css('display', 'block');
      $.get($SCRIPT_ROOT + '/source/get', function(data){
        $('#sourceget').html(data).slideToggle("fast");
        $('#sources_load').css('display', 'none');
        $('html,body').animate({scrollTop: $('#sources').offset().top}, 'slow');
      });
    }
    else{
      $('#sourceget').slideToggle("fast");
    }
  });


  /*
    USAGE SECTION
  */

  $(document).on('click', 'input#usage_raw', function() {
    $.getJSON($SCRIPT_ROOT + '/usage/get_raw', 
    function(data) {
      formatted = output_format(data);
      var html_formatted = usage_output_format_html(formatted);
      $.post($SCRIPT_ROOT + '/usage/set_export', {output:formatted});
      $("#usage_output").html(html_formatted);
    });
    return false;
  });

  $(document).on('click', '#usage_refresh', function() {
    //only get data if we're opening 
    $('#usageget').css('display') == 'none';
    $('#usageget').slideToggle("fast");
    // loading gif
    $('#usage_load').css('display', 'block');
    $.get($SCRIPT_ROOT + '/usage/get', 'reload=1', function(data){
      $('#usageget').html(data).slideToggle("fast");
      $('#usage_load').css('display', 'none');
    });
  });

  // helper functions

  //add the rest of the output html to the formatted output
  var usage_output_format_html = function(formatted){
    var html_formatted = "";
    var clear_output= "<span class='output_control' onclick='document.getElementById(\"usage_output\").innerHTML = \"\";'><a href='#usage'>clear output</a></span>";
    var export_output= "<span class='output_control'><a href='/usage/get_export/output.txt'>export output.txt</a></span>";
    var output_control = "<div class='output_control_container'>" + clear_output + export_output + "</div>";
    html_formatted = "<div class='inner_output'><pre>" + formatted + "</pre></div>" + output_control;

    return html_formatted;
  }


  /*
    ACCOUNT SECTION
  */

    $(document).on('click', 'input#account_raw', function() {
      $.getJSON($SCRIPT_ROOT + '/account/get_raw', 
      function(data) {
        formatted = output_format(data);
        var html_formatted = account_output_format_html(formatted);
        $.post($SCRIPT_ROOT + '/account/set_export', {output:formatted});
        $("#account_output").html(html_formatted);
      });
      return false;
    });

    $(document).on('click', '#account_refresh', function() {
      //only get data if we're opening 
      $('#accountget').css('display') == 'none';
      $('#accountget').slideToggle("fast");
      // loading gif
      $('#account_load').css('display', 'block');
      $.get($SCRIPT_ROOT + '/account/get', 'reload=1', function(data){
        $('#accountget').html(data).slideToggle("fast");
        $('#account_load').css('display', 'none');
      });
    });

    // helper functions

    //add the rest of the output html to the formatted output
    var account_output_format_html = function(formatted){
      var html_formatted = "";
      var clear_output= "<span class='output_control' onclick='document.getElementById(\"account_output\").innerHTML = \"\";'><a href='#account'>clear output</a></span>";
      var export_output= "<span class='output_control'><a href='/account/get_export/output.txt'>export output.txt</a></span>";
      var output_control = "<div class='output_control_container'>" + clear_output + export_output + "</div>";
      html_formatted = "<div class='inner_output'><pre>" + formatted + "</pre></div>" + output_control;

      return html_formatted;
    }


    /* PYLON */

    $(document).on('click', 'input#pylon_raw', function() {
      $.getJSON($SCRIPT_ROOT + '/pylon/get_raw', 
      function(data) {
        formatted = output_format(data);
        var html_formatted = pylon_output_format_html(formatted);
        $.post($SCRIPT_ROOT + '/pylon/set_export', {output:formatted});
        $("#pylon_output").html(html_formatted);
      });
      return false;
    });

    $(document).on('click', 'input#pylon_start', function() {
      var recs = "";
      // NOTE - each checkbox has name like: <hash>_<identity id>
      // split on _ delimeter for user confirmation.
      $( ".pylon:checked").each(function(){
        recs = recs + "\n" + $( this ).attr('name').split('_')[0];
      });
      var confirm_start = confirm("Are you sure you want to start PYLON recordings:\n " + recs);
      if (confirm_start == true){
        pylon_output_wait();
        $.getJSON($SCRIPT_ROOT + '/pylon/start',
        $( ".pylon:checked"), 
        function(data) {
          formatted = pylon_control_output_format(data,"started");
          $("#pylon_output").html(formatted);
          $.each(data.success, function( index, id ){
            $("#status_"+id).text("running")
          });
        });
      }
      return false;
    });

    $(document).on('click', 'input#pylon_stop', function() {
      var recs = "";
      // NOTE - each checkbox has name like: <hash>_<identity id>
      // split on _ delimeter for user confirmation.
      $( ".pylon:checked").each(function(){
        recs = recs + "\n" + $( this ).attr('name').split('_')[0];
      });
      var confirm_stop = confirm("Are you sure you want to stop PYLON recordings:\n " + recs);
      if (confirm_stop == true){
        pylon_output_wait();
        $.getJSON($SCRIPT_ROOT + '/pylon/stop',
        $( ".pylon:checked"), 
        function(data) {
          formatted = pylon_control_output_format(data,"stopped");
          $("#pylon_output").html(formatted);
          $.each(data.success, function( index, id ){
            $("#status_"+id).text("stopped")
          });
        });
      }
      return false;
    });

    $(document).on('click', '#pylon_refresh', function() {
      //only get data if we're opening 
      $('#pylonget').css('display') == 'none';
      $('#pylonget').slideToggle("fast");
      // loading gif
      $('#pylon_load').css('display', 'block');
      $.get($SCRIPT_ROOT + '/pylon/get', 'reload=1', function(data){
        $('#pylonget').html(data).slideToggle("fast");
        $('#pylon_load').css('display', 'none');
      });
    });

    

    // helper functions

    var pylon_output_wait = function(){
      $("#pylon_output").text("[ please wait ]");
    }

    // html formatted success/fail response for push control actions
    var pylon_control_output_format = function(data,action){
      var formatted = ""
      if (data.success.length > 0){
        formatted += action + ":<BR>";
        for (i = 0; i < data.success.length; i++){
          formatted += "<ul>" + data.success[i] + "</ul>";
        }
      }
      if (data.fail.length > 0){
        formatted += "not " + action + ":<BR>";
        for (i = 0; i < data.fail.length; i++){
          var message = "";
          if ('fail_message' in data){
            message = " - " + data.fail_message[i]
          }
          formatted += "<ul>" + data.fail[i] + message + "</ul>";
        }
      }
      return formatted;
    }


    //add the rest of the output html to the formatted output
    var pylon_output_format_html = function(formatted){
      var html_formatted = "";
      var clear_output= "<span class='output_control' onclick='document.getElementById(\"pylon_output\").innerHTML = \"\";'><a href='#pylon'>clear output</a></span>";
      var export_output= "<span class='output_control'><a href='/pylon/get_export/output.txt'>export output.txt</a></span>";
      var output_control = "<div class='output_control_container'>" + clear_output + export_output + "</div>";
      html_formatted = "<div class='inner_output'><pre>" + formatted + "</pre></div>" + output_control;

      return html_formatted;
    }


    /*
      PUSH
    */

    //push subscription actions

    $(document).on('click', 'input#push_raw', function() {
      push_output_wait();
      $.getJSON($SCRIPT_ROOT + '/push/get_raw',
      $( ".push:checked"), 
      function(data) {
        formatted = push_output_format(data);
        var html_formatted = push_output_format_html(formatted);
        $.post($SCRIPT_ROOT + '/push/set_export', {output:formatted});
        $("#push_output").html(html_formatted);
      });
      return false;
    });

    $(document).on('click', 'input#push_log', function() {
      push_output_wait();
      $.getJSON($SCRIPT_ROOT + '/push/log',
      $( ".push:checked"), 
      function(data) {
        formatted = push_output_format(data);
        var html_formatted = push_output_format_html(formatted);
        $.post($SCRIPT_ROOT + '/push/set_export', {output:formatted});
        $("#push_output").html(html_formatted);
      });
      return false;
    });

    $(document).on('click', 'input#push_dpus', function() {
      push_output_wait();
      $.getJSON($SCRIPT_ROOT + '/push/dpus',
      $( ".push:checked"), 
      function(data) {
        formatted = push_output_format(data);
        var html_formatted = push_output_format_html(formatted);
        $.post($SCRIPT_ROOT + '/push/set_export', {output:formatted});
        $("#push_output").html(html_formatted);
      });
      return false;
    });

    $(document).on('click', 'input#push_delete', function() {
      // confirm that we should delete subs before doing it
      var subs = "";
      $( ".push:checked").each(function(){
        subs = subs + "\n" + $( this ).attr('name');
      });
      var confirm_delete = confirm("Are you sure you want to delete subscriptions:\n " + subs);
      // delete subs
      if (confirm_delete == true){
        push_output_wait();
        $.getJSON($SCRIPT_ROOT + '/push/delete',
        $( ".push:checked"), 
        function(data) {
          formatted = push_control_output_format(data,"deleted");
          $("#push_output").html(formatted);
          $.each(data.success, function( index, id ){
            $("#push_row_"+id).remove();
          });
        });
      }
      return false;
    });

    $(document).on('click', 'input#push_stop', function() {
      var subs = "";
      $( ".push:checked").each(function(){
        subs = subs + "\n" + $( this ).attr('name');
      });
      var confirm_delete = confirm("Are you sure you want to stop subscriptions:\n " + subs);
      if (confirm_delete == true){
        push_output_wait();
        $.getJSON($SCRIPT_ROOT + '/push/stop',
        $( ".push:checked"), 
        function(data) {
          formatted = push_control_output_format(data,"stopped");
          $("#push_output").html(formatted);
          $.each(data.success, function( index, id ){
            $("#push_status_"+id).text("stopped")
          });
        });
      }
      return false;
    });

    $(document).on('click', 'input#push_pause', function() {
      push_output_wait();
      $.getJSON($SCRIPT_ROOT + '/push/pause',
      $( ".push:checked"), 
      function(data) {
        formatted = push_control_output_format(data,"paused");
        $("#push_output").html(formatted);
        $.each(data.success, function( index, id ){
          $("#push_status_"+id).text("paused")
        });
      });
      return false;
    });

    $(document).on('click', 'input#push_resume', function() {
      push_output_wait();
      $.getJSON($SCRIPT_ROOT + '/push/resume',
      $( ".push:checked"), 
      function(data) {
        formatted = push_control_output_format(data,"resumed");  
        $("#push_output").html(formatted);
        $.each(data.success, function( index, id ){
          $("#push_status_"+id).text("active")
        });
      });
      return false;
    });

    $(document).on('click', '#push_refresh', function() {
      //only get data if we're opening 
      $('#pushget').css('display') == 'none';
      $('#pushget').slideToggle("fast");
      // loading gif
      $('#push_load').css('display', 'block');
      $.get($SCRIPT_ROOT + '/push/get', 'reload=1', function(data){
        $('#pushget').html(data).slideToggle("fast");
        $('#push_load').css('display', 'none');
      });
    });

    //helper functions

    var push_output_wait = function(){
      $("#push_output").text("[ please wait ]");
    }

    // html formatted success/fail response for push control actions
    var push_control_output_format = function(data,action){
      var formatted = ""
      if (data.success.length > 0){
        formatted += action + ":<BR>";
        for (i = 0; i < data.success.length; i++){
          formatted += "<ul>" + data.success[i] + "</ul>";
        }
      }
      if (data.fail.length > 0){
        formatted += "not " + action + ":<BR>";
        for (i = 0; i < data.fail.length; i++){
          var message = "";
          if ('fail_message' in data){
            message = " - " + data.fail_message[i]
          }
          formatted += "<ul>" + data.fail[i] + message + "</ul>";
        }
      }
      return formatted;
    }

    //stringify the json so that its formatted nicely for output (we export this as well)
    var push_output_format = function(data){
      var formatted = "";

      for (i = 0; i < data.out.length; i++){
        formatted = formatted + JSON.stringify(data.out[i], null, 4) + "\n\n";
      }
      return formatted;
    }

    //add the rest of the output html to the formatted output
    var push_output_format_html = function(formatted){
      var html_formatted = "";
      var clear_output= "<span class='output_control' onclick='document.getElementById(\"push_output\").innerHTML = \"\";'><a href='#push'>clear output</a></span>";
      var export_output= "<span class='output_control'><a href='/push/get_export/output.txt'>export output.txt</a></span>";
      var output_control = "<div class='output_control_container'>" + clear_output + export_output + "</div>";
      html_formatted = "<div class='inner_output'><pre>" + formatted + "</pre></div>" + output_control;

      return html_formatted;
    }


/*  HISTORICS */

//historics subscription actions

    $(document).on('click', 'input#historics_raw', function() {
      historics_output_wait();
      $.getJSON($SCRIPT_ROOT + '/historics/get_raw',
      $( ".historics:checked"), 
      function(data) {
        formatted = historics_output_format(data);
        var html_formatted = historics_output_format_html(formatted);
        $.post($SCRIPT_ROOT + '/historics/set_export', {output:formatted});
        $("#historics_output").html(html_formatted);
      });
      return false;
    });

    $(document).on('click', 'input#historics_log', function() {
      historics_output_wait();
      $.getJSON($SCRIPT_ROOT + '/push/log',
      $( ".historics:checked"), 
      function(data) {
        formatted = historics_output_format(data);
        var html_formatted = historics_output_format_html(formatted);
        $.post($SCRIPT_ROOT + '/historics/set_export', {output:formatted});
        $("#historics_output").html(html_formatted);
      });
      return false;
    });

    $(document).on('click', 'input#historics_dpus', function() {
      historics_output_wait();
      $.getJSON($SCRIPT_ROOT + '/historics/dpus',
      $( ".historics:checked"), 
      function(data) {
        formatted = historics_output_format(data);
        var html_formatted = historics_output_format_html(formatted);
        $.post($SCRIPT_ROOT + '/historics/set_export', {output:formatted});
        $("#historics_output").html(html_formatted);
      });
      return false;
    });

    $(document).on('click', 'input#historics_push_delete', function() {
      var subs = "";
      $( ".historics:checked").each(function(){
        subs = subs + "\n" + $( this ).attr('name');
      });
      var confirm_delete = confirm("Are you sure you want to delete subscriptions:\n " + subs);
      if (confirm_delete == true){
        historics_output_wait();
        $.getJSON($SCRIPT_ROOT + '/push/delete',
        $( ".historics:checked"), 
        function(data) {
          formatted = historics_control_output_format(data,"deleted");
          $("#historics_output").html(formatted);
          //just remove the sub info
          $.each(data.success, function( index, id ){
            $("#historics_row_"+id).find(".sub").text("");
          });
        });
      }
      return false;
    });

    $(document).on('click', 'input#historics_push_stop', function() {
      var subs = "";
      $( ".historics:checked").each(function(){
        subs = subs + "\n" + $( this ).attr('name');
      });
      var confirm_delete = confirm("Are you sure you want to stop subscriptions:\n " + subs);
      if (confirm_delete == true){
        historics_output_wait();
        $.getJSON($SCRIPT_ROOT + '/push/stop',
        $( ".historics:checked"), 
        function(data) {
          formatted = historics_control_output_format(data,"stopped");
          $("#historics_output").html(formatted);
          $.each(data.success, function( index, id ){
            $("#historics_status_"+id + "> .sub").text("stopped")
          });
        });
      }
      return false;
    });

    $(document).on('click', 'input#historics_push_pause', function() {
      historics_output_wait();
      $.getJSON($SCRIPT_ROOT + '/push/pause',
      $( ".historics:checked"), 
      function(data) {
        formatted = historics_control_output_format(data,"paused");
        $("#historics_output").html(formatted);
        $.each(data.success, function( index, id ){
          $("#historics_status_"+id + "> .sub").text("paused")
        });
      });
      return false;
    });

    $(document).on('click', 'input#historics_push_resume', function() {
      historics_output_wait();
      $.getJSON($SCRIPT_ROOT + '/push/resume',
      $( ".historics:checked"), 
      function(data) {
          formatted = historics_control_output_format(data,"resumed");
          $("#historics_output").html(formatted);
          $.each(data.success, function( index, id ){
          $("#historics_status_"+id + "> .sub").text("active")
        });
        });
      return false;
    });

    $(document).on('click', 'input#historics_pause', function() {
      historics_output_wait();
      $.getJSON($SCRIPT_ROOT + '/historics/pause',
      $( ".historics:checked"), 
      function(data) {
        formatted = historics_control_output_format(data,"paused");
        $("#historics_output").html(formatted);
        $.each(data.success, function( index, id ){
          $("#historics_status_"+id + "> .hist").text("paused")
        });
      });
      return false;
    });

    $(document).on('click', 'input#historics_resume', function() {
      historics_output_wait();
      $.getJSON($SCRIPT_ROOT + '/historics/resume',
      $( ".historics:checked"), 
      function(data) {
        formatted = historics_control_output_format(data,"running");
        $("#historics_output").html(formatted);
        $.each(data.success, function( index, id ){
          $("#historics_status_"+id + "> .hist").text("running")
        });
      });
      return false;
    });

    $(document).on('click', 'input#historics_stop', function() {
      var hists = "";
      $( ".historics:checked").each(function(){
        hists = hists + "\n" + $( this ).attr('name');
      });
      var confirm_stop = confirm("Are you sure you want to stop historics:\n " + hists);
      if (confirm_stop == true){
        historics_output_wait();
        $.getJSON($SCRIPT_ROOT + '/historics/stop',
        $( ".historics:checked"), 
        function(data) {
          formatted = historics_control_output_format(data,"stopped");
          $("#historics_output").html(formatted);
          $.each(data.success, function( index, id ){
            $("#historics_status_"+id + "> .hist").text("stopped")
          });
        });
      }
      return false;
    });

    $(document).on('click', 'input#historics_delete', function() {
      var hists = "";
      $( ".historics:checked").each(function(){
        hists = hists + "\n" + $( this ).attr('name');
      });
      var confirm_delete = confirm("Are you sure you want to delete historics:\n " + hists);
      if (confirm_delete == true){
        historics_output_wait();
        $.getJSON($SCRIPT_ROOT + '/historics/delete',
        $( ".historics:checked"), 
        function(data) {
          formatted = historics_control_output_format(data,"deleted");
          $("#historics_output").html(formatted);
          $.each(data.success, function( index, id ){
            $("#historics_row_"+id).find(".hist").text("");
          });
        });
      }
      return false;
    });

    $(document).on('click', '#historics_refresh', function() {
      $('#historicsget').css('display') == 'none';
      $('#historicsget').slideToggle("fast");
      // loading gif
      $('#historics_load').css('display', 'block');
      $.get($SCRIPT_ROOT + '/historics/get', 'reload=1', function(data){
        $('#historicsget').html(data).slideToggle("fast");
          $('#historics_load').css('display', 'none');
      });
    });

    //helper functions

    var historics_output_wait = function(){
      $("#historics_output").text("[ please wait ]");
    }

    // html formatted success/fail response for push control actions
    var historics_control_output_format = function(data,action){
      var formatted = ""
      if (data.success.length > 0){
        formatted += action + ":<BR>";
        for (i = 0; i < data.success.length; i++){
          formatted += "<ul>" + data.success[i] + "</ul>";
        }
      }
      if (data.fail.length > 0){
        formatted += "not " + action + ":<BR>";
        for (i = 0; i < data.fail.length; i++){
          var message = "";
          if ('fail_message' in data){
            message = " - " + data.fail_message[i]
          }
          formatted += "<ul>" + data.fail[i] + message + "</ul>";
        }
      }
      return formatted;
    }

    //stringify the json so that its formatted nicely for output (we export this as well)
    var historics_output_format = function(data){
      var formatted = "";

      for (i = 0; i < data.out.length; i++){
        formatted = formatted + JSON.stringify(data.out[i], null, 4) + "\n\n";
      }
      return formatted;
    }

    //add the rest of the output html to the formatted output
    var historics_output_format_html = function(formatted){
      var html_formatted = "";
      var clear_output= "<span class='output_control' onclick='document.getElementById(\"historics_output\").innerHTML = \"\";'><a href='#historics'>clear output</a></span>";
      var export_output= "<span class='output_control'><a href='/get_historics_export/output.txt'>export output.txt</a></span>";
      var output_control = "<div class='output_control_container'>" + clear_output + export_output + "</div>";
      html_formatted = "<div class='inner_output'><pre>" + formatted + "</pre></div>" + output_control;

      return html_formatted;
    }

/*  
  MANAGED SOURCES
*/

//Managed Sources actions

    $(document).on('click', 'input#source_raw', function() {
      source_output_wait();
      $.getJSON($SCRIPT_ROOT + '/source/get_raw',
      $( ".source:checked"), 
      function(data) {
        formatted = source_output_format(data);
        var html_formatted = source_output_format_html(formatted);
        $.post($SCRIPT_ROOT + '/source/set_export', {output:formatted});
        $("#source_output").html(html_formatted);
      });
      return false;
    });

    $(document).on('click', 'input#source_log', function() {
      source_output_wait();
      $.getJSON($SCRIPT_ROOT + '/source/log',
      $( ".source:checked"), 
      function(data) {
        formatted = source_output_format(data);
        var html_formatted = source_output_format_html(formatted);
        $.post($SCRIPT_ROOT + '/source/set_export', {output:formatted});
        $("#source_output").html(html_formatted);
      });
      return false;
    });

    $(document).on('click', 'input#source_delete', function() {
      var srcs = "";
      $( ".source:checked").each(function(){
        srcs = srcs + "\n" + $( this ).attr('name');
      });
      var confirm_delete = confirm("Are you sure you want to delete Managed Sources:\n " + srcs);
      if (confirm_delete == true){
        source_output_wait();
        $.getJSON($SCRIPT_ROOT + '/source/delete',
        $( ".source:checked"), 
        function(data) {
          formatted = source_control_output_format(data,"deleted");
          $("#source_output").html(formatted);
          $.each(data.success, function( index, id ){
            $("#source_row_"+id).remove()
          });
        });
      }
      return false;
    });

    $(document).on('click', 'input#source_stop', function() {
      source_output_wait();
      $.getJSON($SCRIPT_ROOT + '/source/stop',
      $( ".source:checked"), 
      function(data) {
        formatted = source_control_output_format(data,"stopped");
        $("#source_output").html(formatted);
        $.each(data.success, function( index, id ){
          $("#status_"+id).text("stopped")
        });
      });
      return false;
    });


    $(document).on('click', 'input#source_start', function() {
      source_output_wait();
      $.getJSON($SCRIPT_ROOT + '/source/start',
      $( ".source:checked"), 
      function(data) {
        formatted = source_control_output_format(data,"started");
        $("#source_output").html(formatted);
        $.each(data.success, function( index, id ){
          $("#status_"+id).text("running")
        });
      });
      return false;
    });

    //load new tokens to Managed Sources

    $(document).on('click', 'input#source_token', function() {
      var formatted = ""
      for (i=0; i < $( ".source:checked").length; i++){
        formatted = formatted + "<li>" + $( ".source:checked")[i].name + ' <input type="text" class=token name=' + $( ".source:checked")[i].name + ">" + "</li>";
      }
      
      if ($( ".source:checked").length > 0) {
        formatted = formatted + '<input type="button" value="Submit" id="token_submit" >';
        $("#source_submit").show();
      }
      
      $("#source_output").html(formatted);
      return false;
    });

    // doesn't work because #source_output isn't available yet.
    $('#source_output').on('click', '#token_submit', function() {
      source_output_wait();
      $.getJSON($SCRIPT_ROOT + '/source/token',
      $( ".token:text"), 
      function(data) {
        formatted = source_control_output_format(data,"added");
        $("#source_output").html(formatted);
        $.each(data.success, function( index, id ){
          $("#status_"+id).text("running")

        });
      });
      return false;
    });

    $(document).on('click', '#source_refresh', function() {
      $('#sourceget').css('display') == 'none';
      $('#sourceget').slideToggle("fast");
      // loading gif
      $('#sources_load').css('display', 'block');
      $.get($SCRIPT_ROOT + '/source/get', 'reload=1', function(data){
        $('#sourceget').html(data).slideToggle("fast");
        $('#sources_load').css('display', 'none');
      });
    });


    //helper functions

    var source_output_wait = function(){
      $("#source_output").text("[ please wait ]");
    }

    // html formatted success/fail response for push control actions
    var source_control_output_format = function(data,action){
      var formatted = ""
      if (data.success.length > 0){
        formatted += action + ":<BR>";
        for (i = 0; i < data.success.length; i++){
          formatted += "<ul>" + data.success[i] + "</ul>";
        }
      }
      if (data.fail.length > 0){
        formatted += "not " + action + ":<BR>";
        for (i = 0; i < data.fail.length; i++){
          var message = "";
          if ('fail_message' in data){
            message = " - " + data.fail_message[i]
          }
          formatted += "<ul>" + data.fail[i] + message + "</ul>";
        }
      }
      return formatted;
    }

    //stringify the json so that its formatted nicely for output (we export this as well)
    var source_output_format = function(data){
      var formatted = "";

      for (i = 0; i < data.out.length; i++){
        formatted = formatted + JSON.stringify(data.out[i], null, 4) + "\n\n";
      }
      return formatted;
    }

    //add the rest of the output html to the formatted output
    var source_output_format_html = function(formatted){
      var html_formatted = "";
      var clear_output= "<span class='output_control' onclick='document.getElementById(\"source_output\").innerHTML = \"\";'><a href='#sources'>clear output</a></span>";
      var export_output= "<span class='output_control'><a href='/get_source_export/output.txt'>export output.txt</a></span>";
      var output_control = "<div class='output_control_container'>" + clear_output + export_output + "</div>";
      html_formatted = "<div class='inner_output'><pre>" + formatted + "</pre></div>" + output_control;

      return html_formatted;
    }


/* COMMON things */

    //update ratelimit
    $(document).on('click', ':button,h3', function() {
      $.get($SCRIPT_ROOT + '/update_ratelimit', function(data){
        $('#ratelimit').text(data);
      });
    });

    //stringify the json so that its formatted nicely for output (we export this as well)
    var output_format = function(data){
      return JSON.stringify(data.out, null, 4);
    }

});
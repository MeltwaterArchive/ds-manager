$(document).ready(function() {
  // INITIALIZE - remove push and sources session info on page load
  $.get($SCRIPT_ROOT + '/reset_usage');
  $.get($SCRIPT_ROOT + '/reset_account');
  $.get($SCRIPT_ROOT + '/reset_pylon');
  $.get($SCRIPT_ROOT + '/reset_push');
  $.get($SCRIPT_ROOT + '/reset_historics');
  $.get($SCRIPT_ROOT + '/reset_sources');

  if( $("#usage").length == 0 ) {
    $('#login_button').val("Log in")
  }
  else {
    $('#login_button').val("Switch users")
  }

  $.get($SCRIPT_ROOT + '/usage_get', function(data){
    $('#usage_load').css('display', 'none');
    $('#usageget').html(data);
  });

  // hide/show tables
  $('#usage').click(function() {
    //only get data if we're opening 
    if ($('#usageget').css('display') == 'none'){
      // loading gif
      $('#usage_load').css('display', 'block');
      $.get($SCRIPT_ROOT + '/usage_get', function(data){
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
      $.get($SCRIPT_ROOT + '/account_get', function(data){
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
      $.get($SCRIPT_ROOT + '/pylon_get', function(data){
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
      $.get($SCRIPT_ROOT + '/push_get', function(data){
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
      $.get($SCRIPT_ROOT + '/historics_get', function(data){
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
      $.get($SCRIPT_ROOT + '/source_get', function(data){
        $('#sourceget').html(data).slideToggle("fast");
        $('#sources_load').css('display', 'none');
        $('html,body').animate({scrollTop: $('#sources').offset().top}, 'slow');
      });
    }
    else{
      $('#sourceget').slideToggle("fast");
    }
  });

});
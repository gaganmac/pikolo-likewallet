function main(){

	//Initialize tooltips
	$(function () {
	  $('[data-toggle="tooltip"]').tooltip()
	})

	/* URL formatting for registration form (not working)

	$(document).on("submit", "#formRegister", function(e){

		event.preventDefault();
		url = $("#companyWebsite").val();
		if (url.match("^http")) {
			$("#formRegister").submit();
		}
		else {
			$("#companyWebsite").val("http://" + url);
			alert(("#companyWebsite").val())
			$("#formRegister").submit();
		}

	}); */

	//DASHBOARD PAGE
	$("#posts").on("activate.bs.scrollspy", function () {
	  	alert("test");
	  	//Open modal for new post
		$("#modal-new-post").modal("show");
		$('.modal-backdrop').appendTo("#001");   
		//remove the padding right and modal-open class from the body tag which bootstrap adds when a modal is shown
		$('body').removeClass("modal-open")
		$('body').css("padding-right","");
		//Close modal when cost is submitted
		$(document).on("submit", "#form-cost", function(){
			$(".modal").modal("hide");
			return false;
		});
	})

	// Add smooth scrolling on all links inside dashboard navigation
	$("#nav-dashboard a").on('click', function(event) {

	  // Make sure this.hash has a value before overriding default behavior
	  if (this.hash !== "") {

	    // Prevent default anchor click behavior
	    event.preventDefault();

	    // Store hash
	    var hash = this.hash;

	    // Using jQuery's animate() method to add smooth page scroll
	    // The optional number (800) specifies the number of milliseconds it takes to scroll to the specified area
	    $('html, body').animate({
	      scrollTop: $(hash).offset().top
	    }, 800, function(){

	    // Add hash (#) to URL when done scrolling (default click behavior)
	      window.location.hash = hash;
	    });

	  } // End if

	});

	//Show add influencer modal on dashboard if user has zero influencers
	$("#modalZeroInfluencers").modal("show");

	//Get tracking keyword entered by user
	$(document).on("submit", "#formKeyword", function(e){

		//prevent form submission
		e.preventDefault();
		//Add loading spinner
		$("#formKeyword > .loadSpinner").show();
		//disable track button
		$(".keyword-btn").attr("disabled", true);
		//store keyword in database
		var keyword = $("#campaignHandle").val();
		$.post($SCRIPT_ROOT + '/addkeyword', {"keyword" : keyword})
		//Submit form and refresh page after keyword is stored succesfully
		.done(function(result){
			$("#formKeyword").submit();
			location.reload();
		});

	});

	//Removing tracking keyword
	$(document).on("click", ".chip .close", function(){
		//Hide chip
		$(this).parent().hide();
		//Add loading spinner
		$("#formKeyword > .loadSpinner").show();
		//disable track button
		$(".keyword-btn").attr("disabled", true);
		//store empty keyword in database
		var keyword = "";
		$.post($SCRIPT_ROOT + '/addkeyword', {"keyword" : keyword})
		//refresh page
		.done(function(result){
			location.reload();
		});


	});

	//INFLUENCERS PAGE

	//Hide elements
	$(".add-group-menu").hide();
	$('#invalid').hide();
	$('#duplicate').hide();
	$('#privateProfile').hide();


	//Add new influencer (e.g.Selena Gomez)
	$(document).on("submit", "#formAddInfluencer", function(e){

		e.preventDefault();
		//Add loading spinner
		$("#formAddInfluencer > .loadSpinner").show();
		//disable button
		$(".add-influencer-btn").attr("disabled", true);
		//Get username
		var username = $("#formInfluencerHandle").val();
		
		//remove "@" if user inputted it
		if (username.charAt(0) == "@") {
			username = username.substring(1);
		}

		$.ajax({
        url: "https://cors-anywhere.herokuapp.com/" + "http://instagram.com/" + username + "/media/",        //get JSON from specific user
        dataType: "json",
        success: function(data) {

			if (data.items.length == 0) {
				$('#invalid').hide();
        	 	$('#duplicate').hide();
        	 	$('#privateProfile').show();
        	 	//Hide loading spinner
				$("#formAddInfluencer > .loadSpinner").hide();
				//Enable button
				$(".add-influencer-btn").attr("disabled", false);
			}

			else if (data.items[0].user && $(".influencer-list:contains('" + data.items[0].user.full_name + "')" ).length > 0) { //influencer already added
        	 	$('#invalid').hide();
        	 	$('#privateProfile').hide()
        	 	$('#duplicate').show();
        	 	//Hide loading spinner
				$("#formAddInfluencer > .loadSpinner").hide();
				//Enable button
				$(".add-influencer-btn").attr("disabled", false);

			} 

        	else {

        	 	
        	 	var posts;
        	 	var followers;
        	 	var profilePicture = data.items[0].user.profile_picture
        	 	var fullName = data.items[0].user.full_name
        	 	var username = data.items[0].user.username
        	 	$.get("https://cors-anywhere.herokuapp.com/" + "http://instagram.com/" + username, function(data) {
        	 		console.log(data.split(' ')[716])
        	 		var array = data.split(' ')
        	 		followers = array[array.indexOf('Followers,') - 1].split('"')[1]
        	 		posts = array[array.indexOf('Posts') - 1]
        	 		
        	 		$("#influencers .influencer-list").append('<div href="#" class="list-group-item list-group-item-action d-flex justify-content-start flex-nowrap"><img class="img-fluid rounded-circle" src=' + profilePicture  + '><div class="d-flex justify-content-start flex-wrap"><div class="influencer-name"><strong>' + fullName + '</strong></div><div class="extra-margin-right"><small>'+ followers + ' followers</small></div><div class="extra-margin-right"><small>' + posts + ' posts</small></div></div><div class="ml-auto d-flex flex-nowrap"><a href="https://www.instagram.com/' + username + '/"' +  ' target="_blank"><i class="fa fa-instagram btn-influencer"></i></a><a href="https://www.instagram.com/audreylombard/" target="_blank"><i class="fa fa-facebook btn-influencer" style="color:#E0E0E0;"></i></a><a href="https://www.instagram.com/audreylombard/" target="_blank"><i class="fa fa-twitter btn-influencer" style="color:#E0E0E0;"></i></a><a href="https://www.instagram.com/audreylombard/" target="_blank"><i class="fa fa-snapchat btn-influencer" style="color:#E0E0E0;"></i></a><a class="remove-influencer-btn btn-influencer"><i class="fa fa-trash-o"></i></a>');
        			$.post($SCRIPT_ROOT + '/addinfluencer', {"handle" : username, "followers" : followers})
					$("#modalZeroInfluencers").modal("hide");
					$('#add-influencers').modal('hide');
        			$('#duplicate').hide();
        	 		$('#invalid').hide();
        	 		$('#privateProfile').hide()
        	 		//Hide loading spinner
					$("#formAddInfluencer > .loadSpinner").hide();
					//Enable button
					$(".add-influencer-btn").attr("disabled", false);
        	 	});
        			
        	}
        	
        	
        }, error: function(error) {      //influencer does not exist
        	$('#duplicate').hide();
        	$('#privateProfile').hide()
        	$('#invalid').show();
        	//Hide loading spinner
			$("#formAddInfluencer > .loadSpinner").hide();
			//Enable button
			$(".add-influencer-btn").attr("disabled", false);
  },

     });

        
	});

	$(document).on("hidden.bs.modal", "#modalZeroInfluencers", function(){
		location.reload();
	});

	//Close add influencer modal
	$('#add-influencers').on('hidden.bs.modal', function() {
        $('#duplicate').hide();
        $('#invalid').hide();
	});


	//Remove an influencer
	$(document).on("click", ".remove-influencer-btn", function(){
		var accountLink = $(this).parent().children().first().attr('href');
		var handle = accountLink.split('https://www.instagram.com/')[1].split('/')[0];


		$(this).parentsUntil(".influencer-list")
			.slideToggle(400, function(){
				$(this).remove()});

		$.post($SCRIPT_ROOT + '/removeinfluencer', {"handle" : handle});
	});

	//Create a new influencer group 
	$(document).on("click", ".create-group-btn", function(){

		var newGroup = true;
		
		//Hide search filters
		$(".influencer-filters").slideUp();
		//Show nav for creating new group
		$(".add-group-menu").slideDown();
		//Hide buttons on influencer cards
		$(".btn-influencer").fadeOut("fast");
		//Disable appropriate buttons
		$(".btn-block, .dropdown-toggle").attr("disabled", true);
		
		//Select influencers and enable create button
		$(document).on("click", ".list-group-item-action", function(){
			if(newGroup){
				$(this).toggleClass("active");
				$(".btn-group-create").attr("disabled", false);
			}
		});

		//Submit group form
		$(document).on("submit", ".formGroupName", function(){
			var newGroup = $("#groupInput").val()
			$(".influencer-groups").append('<a class="dropdown-item" href="#">'+ newGroup +'</a>');
			//Empty form fields
			$("#groupInput").val("");
			//Unselect influencers
			$(".list-group-item-action").removeClass("active");
			//generate success alert, fade it out, and remove it from DOM
			$(".alerts-container").prepend('<div class="alert alert-success animated fadeInDown" role="alert">New group created</div>')
			setTimeout(
			  function() 
			  {
			    $(".alert").addClass("fadeOut");
			  }, 1500);
			setTimeout(
			  function() 
			  {
			    $(".alert").alert("close");
			  }, 2000);


		});

		//Close new group nav
		$(document).on("click", ".btn-group-cancel", function(){
				
			//Disable create group button
			$(".btn-group-create").attr("disabled", true);
			//Unselect all influencers
			$(".list-group-item-action").removeClass("active");
			//Empty form fields
			$("#groupInput").val("");		
			//Enable button 'add influencers' & 'groups'  
			$(".btn-block, .dropdown-toggle").attr("disabled", false);			
			//Show search filters
			$(".influencer-filters").slideDown();
			//Hide navbar for creating new group
			$(".add-group-menu").slideUp();
			//Show buttons on influencer cards
			$(".btn-sm").fadeIn("fast");

			newGroup = false;

		});

	});

};

$(document).ready(main);
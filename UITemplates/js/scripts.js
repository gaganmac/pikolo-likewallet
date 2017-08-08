function main(){

	//Hide elements
	$(".add-group-menu").hide();


	//Add new influencer Selena Gomez
	$(document).on("click", ".add-influencer-btn", function(){
		$(".influencer-list").append('<div href="#" class="list-group-item list-group-item-action d-flex justify-content-start flex-nowrap"><img class="img-fluid rounded-circle" src="https://scontent-cdg2-1.cdninstagram.com/t51.2885-19/s320x320/19955667_1078934505542036_6745075692590858240_a.jpg"><div class="d-flex justify-content-start flex-wrap"><div class="influencer-name"><strong>Selena Gomez</strong></div><div class="extra-margin-right"><small>124m followers</small></div><div class="extra-margin-right"><small>1,352 posts</small></div></div><div class="ml-auto d-flex flex-nowrap"><a href="https://www.instagram.com/selenagomez/" target="_blank" class="btn btn-default btn-sm"><i class="fa fa-instagram"></i></a><a class="remove-influencer-btn btn btn-blue-grey btn-sm"><i class="fa fa-trash-o"></i></a></div></div>');
	});

	//Remove influencer
	$(document).on("click", ".remove-influencer-btn", function(){
		$(this).parentsUntil(".influencer-list")
			.slideToggle(400, function(){
				$(this).remove()});
	});

	//Initialize boolean for creating new groups
	//var newGroup = false;

	//Open interface to create new group 
	$(document).on("click", ".create-group-btn", function(){

		var newGroup = true;
		
		//Hide search filters
		$(".influencer-filters").slideUp();
		//Show navbar for creating new group
		$(".add-group-menu").slideDown();
		//Hide buttons on influencer cards
		$(".btn-sm").fadeOut("fast");
		//Disable appropriate buttons
		$(".btn-block, .dropdown-toggle").attr("disabled", true);
		
		//Select influencers and enable create button
		$(document).on("click", ".list-group-item-action", function(){
			if(newGroup){
				$(this).toggleClass("active");
				$(".btn-group-create").attr("disabled", false);
			}
		});

		//Empty group name field and unselect influencers after submitting group form
		$(document).on("submit", "#formGroupName", function(){
			$(".form-control").val("");
			$(".list-group-item-action").removeClass("active");
			$(".alerts-container").append('<div class="alert alert-success fade show" role="alert">New group created</div>')
			//$(".alert").fadeIn().delay(2000).fadeOut();
		});

		//Close interface to create new group
		$(document).on("click", ".btn-group-cancel", function(){
				
			//Disable create group button
			$(".btn-group-create").attr("disabled", true);
			//Unselect all influencers
			$(".list-group-item-action").removeClass("active");		
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
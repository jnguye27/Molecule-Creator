/* javascript to accompany .html pages for Assignment 4 

   Student Name: Jessica Nguyen
   Student ID: 1169812
   Due Date: April 5th, 2023 
   Course: CIS*2750 
*/

$(document).ready( 
	/* This defines a function that gets called after the document is in memory */
	function()
	{
      /* Reload select element options (when refreshing the page) */
		$.post("/reload_elements.html", { reload: "element" },
         function( data )
         {
            /* Update the element list (if the element is in the database) */
            if (data.search("Invalid") == -1)
            {
               /* 0 & odds = str, 1 & evens = code */
               var splitElements = data.split(" ")
               for (let i = 0; i < splitElements.length; i++)
               {
                  var splitstr1 = splitElements[i].concat(" ", splitElements[i+1]);

                  $("#elementList").append(
                     $('<option></option>').attr("value", splitElements[i+1][1]).text(splitstr1)
                  );

                  i++;
               }
            }
         }
      );

      /* Reload select molecule options (when refreshing the page) */
		$.post("/reload_molecules.html", { reload: "molecule" },
         function( data )
         {
            /* Update the molecule list (if the molecule is in the database) */
            if (data.search("Invalid") == -1)
            {
               var splitMolecules = data.split(" ")
               for (let i = 0; i < splitMolecules.length; i++)
               {
                  $("#moleculeList").append(
                     $('<option></option>').attr("value", splitMolecules[i]).text(splitMolecules[i])
                  );
               }
            }
         }
      );

		/* Hide pop-up messages */
      $("#displayMolecule").hide();

		/* Button saves element data from the user when clicked */
		$("#addButton").click(
			function()
			{
            var elementText1 = document.getElementById("elementName").value;
            var elementText2 = document.getElementById("elementCode").value;
            var elementStr = elementText1.concat(" (", elementText2,")");

				/* Redirect the data to the server's do_POST */
				$.post("/add_element.html",
					/* Pass data as a JavaScript dictionary */
					{
                  elementNum: $("#elementNum").val(),
                  elementCode: $("#elementCode").val(),
                  elementName: $("#elementName").val(),
                  colourOne: $("#colourOne").val(),
                  colourTwo: $("#colourTwo").val(),
                  colourThree: $("#colourThree").val(),
                  radius: $("#radius").val()
					},
					function( data )
					{
                  /* Sends the user a notification (did it work?) */
                  /*alert(data)*/
                  $("#status4").text(data);
                  
                  /* Add to the element list (if the element is valid) */
                  if (data.search("Invalid") == -1)
                  {
                     $("#elementList").append(
                        $('<option></option>').attr("value", elementText2).text(elementStr)
                     );
                  }
					}
				);

            /* Empty the input values */
            $("#elementNum").val("");
            $("#elementCode").val("");
            $("#elementName").val("");
            $("#colourOne").val("");
            $("#colourTwo").val("");
            $("#colourThree").val("");
            $("#radius").val("");
			}
		);

		/* Button deletes element data by the user when clicked */
		$("#removeButton").click(
			function()
			{
            /* Button only works if an option is selected in elementList */
            $("#elementList option:selected").each(
               function()
               {  
                  /* Redirect the data to the server's do_POST */
                  $.post("/remove_element.html",

                     /* Pass as a JavaScript dictionary */
                     {
                        selectElement: $(this).text()
                     },
                     function( data )
                     {
                        /* Sends the user a notification */
                        /*alert(data);*/
                        
                        /* Remove the selected element from the list */
                        if (data.search("Invalid") == -1)
                        {
                           $("#elementList option:selected").remove();
                        }
                     }
                  );
               }
            );
			}
		);
      
      /* Button uploads molecule data from the user when clicked */
		$("#uploadButton").click(
			function()
			{
            var uploadText = document.getElementById("molName").value;

				/* Redirect the data to the server's do_POST */
				$.post("/upload_molecule.html",
					/* Pass as a JavaScript dictionary */
					{
                  molUpload: $("#sdf_file").val(),
                  molName: $("#molName").val()
					},
					function( data )
					{
                  /* Sends the user a notification */
                  /*alert(data);*/
                  $("#status5").text(data);
                  
                  /* Add to the molecule selection list (if it's valid) */
                  if (data.search("Invalid") == -1)
                  {
                     $("#moleculeList").append(
                        $('<option></option>').attr("value", uploadText).text(uploadText)
                     );
                  }
					}
				);

            /* Empty the input values */
            $("#sdf_file").val("");
            $("#molName").val("");
			}
		);

      /* Selected molecule options will show atom and element amount */
      $("#moleculeList").change(
         function()
         {
            $("#moleculeList option:selected").each(
               function()
               {
                  var selectText = $(this).text();

                  /* Redirect the data to the server's do_POST */
                  $.post("/select_molecule1.html",
                     /* Pass as a JavaScript dictionary */
                     {
                        selected: $(this).text()
                     },
                     function( data )
                     {
                        /* Output the selected option's atom and bond number */
                        var splitData = data.split(" ");
                        $("#status1").text(splitData[0]);
                        $("#status2").text(splitData[1]);
                        $("#status3").text(selectText);
                     }
                  );
               }
            );
         } 
      );

      /* Select a molecule when the user clicks the select button */
      $("#selectButton").click(
			function()
			{
            $("#moleculeList option:selected").each(
               function()
               {  
                  /* Redirect the data to the server's do_POST */
                  $.post("/select_molecule2.html",
                     /* Pass as a JavaScript dictionary */
                     {
                        selectMolecule: $(this).text()
                     },
                     function( data )
                     {
                        /* Notify the user (did it work?) */
                        /*alert(data);*/
                        $("#status6").text(data);
                     }
                  );
               }
            );
			}
		);

      /* Button displays the molecule that the user selected when clicked */
		$("#displayButton").click(
			function()
			{
				/* Sends a notification, redirects the data to the server's do_POST */
				$.post("/display_molecule_msg.html",
					/* Pass as a JavaScript dictionary */
					{
                  mol: "mol"
					},
					function( data )
					{
                  /* Notify the user (did it work?) */
                  /*alert(data);*/

                  if (data.search("No molecules were selected for display.") == -1)
                  {
                     $("#status7").css("font-weight", "bold");
                     $("#status7").css("font-size", "35px");
                  }

                  $("#status7").text(data);
					}
				);

            /* Obtain the SVG, redirect the data to the server's do_POST */
				$.post("/display_molecule_pic.html",
               /* Pass as a JavaScript dictionary */
               {
                  mol: "mol"
               },
               function( data )
               {  
                  /* If there is a selected molecule, display it */
                  if (data.search("No display.") == -1)
                  {
                     $("#displayMolecule").html(data);
                     $("#displayMolecule").fadeToggle(1000);
                  }
               }
            );
			}
		);
	}
);
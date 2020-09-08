console.log("Sanity check!");

// Get Stripe publishable key
fetch("/config")
  .then((result) => { return result.json(); })
  .then((data) => {
    // Initialize Stripe.js
    const stripe = Stripe(data.publicKey);
  

    // Event handler
    var paymentSelect = document.getElementsByClassName("submitBtn");

    function event() {
      //get subcriber plan
      var subPlan = this.dataset.subcriber;

      // Get Checkout Session ID
      fetch("/create-checkout-session/"+subPlan)
        .then((result) => { return result.json(); })
        .then((data) => {
          console.log(data);
          // Redirect to Stripe Checkout
          return stripe.redirectToCheckout({ sessionId: data.sessionId })
        })
        .then((res) => {
          console.log(res);
        });
    }

    //click choose options
    for (var i = 0; i < paymentSelect.length; i++) {
      paymentSelect[i].addEventListener('click', event, false);
    }

    
  });



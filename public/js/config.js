// Edit this file to change prices, limited-lot quantities and checkout links.
window.CHOCOPUMP = {
  models: {
    pro:    { name: "Chocopump PRO",    price: 569, lotUnits: 30, soldOut: false, checkout: "" },
    deluxe: { name: "Chocopump DELUXE", price: 599, lotUnits: 40, soldOut: false, checkout: "" },
  },
  // checkout: paste each Stripe Payment Link (Whimgoods LLC account). Set "Limit the number of payments"
  // on the link to lotUnits so Stripe stops selling when the lot is gone.
  // While a checkout link is empty, the buy button opens the reserve form instead.
  contactEmail: "info@chocopump.com",
};

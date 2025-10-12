// domain/actions.js
// Policy/config differences between actions. No DOM or network here.

export const ACTIONS = {
  exclude: {
    title: "Escolha a hora que deseja excluir:",
    needsHour: true,
    hoursCRM: (ctx) => ctx.cardCrm,
    endpointAction: 'exclusion',
  },

  ask_for_donation: {
    title: "Escolha a hora que deseja pedir:",
    needsHour: true,
    hoursCRM:  (ctx) => ctx.cardCrm,
    endpointAction: 'ask_for_donation',
  },

  offer_donation: {
    title: "Escolha a hora que deseja oferecer:",
    needsHour: true,
    hoursCRM: (ctx) => ctx.cardCrm,
    endpointAction: 'offer_donation',
  },

  include: {
    title: "Escolha o profissional a ser incluído:",
    title2: "Escolha a hora em que deseja Incluí-lo:",
    needsNames: true,
    needsHour: false,
    hoursCRM: (ctx) => ctx.cardCrm,
    endpointAction: 'include',
  },

  exchange: {
    title: "", // Choose when writing this function
    needsHour: true,
    hoursCRM: (ctx) => ctx.cardCrm,
    endpointAction: () => 'exchange',
  },
};

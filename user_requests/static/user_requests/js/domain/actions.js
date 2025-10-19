// domain/actions.js
// Policy/config differences between actions. No DOM or network here.

export const ACTIONS = {
  SCHexclude: {
    title: "Escolha a hora que deseja excluir:",
    needsHour: true,
    hoursCRM: (ctx) => ctx.cardCrm, // uneeded in schedule context
    endpointAction: 'exclude',
  },

  SCHinclude: {
    title1: "Escolha o Centro que deseja incluir:",
    title2: "Escolha o Dia que deseja incluir:",
    title3: "Escolha a hora que deseja Incluir:",
    needsHour: false,
    hoursCRM: (ctx) => ctx.cardCrm,
    endpointAction: 'include',
  },

  SCHdonate: {
    title1: "Escolha o Horário que deseja Doar:",
    title2: "Escolha para quem deseja Doar:",
    needsHour: true,
    needsNames: true,
    hoursCRM: (ctx) => ctx.cardCrm,
    endpointAction: 'offer_donation',
  },
  
  exclude: {
    title: "Escolha a hora que deseja excluir:",
    needsHour: true,
    hoursCRM: (ctx) => ctx.cardCrm,
    endpointAction: 'exclude',
  },

  ask_for_donation: {
    title: "Escolha a hora que deseja pedir:",
    needsHour: true,
    hoursCRM:  (ctx) => ctx.cardCrm,
    endpointAction: 'ask_for_donation',
  },

  offer_donation: {
    title1: "Escolha o Horário que deseja Doar:",
    title2: "Escolha para quem deseja Doar:",
    needsHour: true,
    needsNames: true,
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

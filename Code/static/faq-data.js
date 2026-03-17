const HELP_DATA = [

/* ==========================================================
   LAND & PROPERTY (20)
========================================================== */
{
  category: "Land & Property",
  questions: [

    {
      question: "Are digitally signed land records legally valid?",
      answer: `Yes. Digitally signed land records obtained through authorized government portals after payment of prescribed fees are legally valid and recognized by the government. 
They carry the same legal weight as traditional paper records and are generally admissible in courts as valid evidence.`
    },

    {
      question: "Which documents are required to be compulsorily registered?",
      answer: `Documents relating to sale, gift, mortgage, or lease of immovable property must be compulsorily registered under Section 17 of the Registration Act, 1908.
Each State may have additional compulsory registration requirements under its respective laws. Unregistered documents that require compulsory registration may become invalid and inadmissible in court.`
    },

    {
      question: "Why is title verification necessary before buying property?",
      answer: `Title verification confirms whether the seller is the legal owner of the property. It checks how ownership was acquired (sale, gift, inheritance, or will) and ensures that the ownership chain is continuous and valid.
Defective title may result in future disputes, cancellation of registration, or financial loss.
(Transfer of Property Act, 1882 – Sections 7 and 8)`
    },

    {
      question: "Does an Agreement to Sell give ownership rights?",
      answer: `No. An Agreement to Sell is only a promise to transfer property in the future. Ownership is transferred only through a Registered Sale Deed.
(Transfer of Property Act, 1882 – Section 54; Registration Act, 1908 – Section 17)`
    },

    {
      question: "Why is property registration compulsory?",
      answer: `Registration gives legal recognition to property transactions. Transfer of immovable property above the prescribed value is not valid without registration.
It makes the document admissible in court and protects parties from fraud and disputes.
(Registration Act, 1908 – Section 17)`
    },

    {
      question: "What are the risks of paying less stamp duty?",
      answer: `If stamp duty is paid insufficiently, the document becomes defective. The government may impose penalties and additional charges.
Courts may refuse to admit such document as valid evidence.
(Indian Stamp Act, 1899)`
    },

    {
      question: "Why is land use verification required?",
      answer: `Land must be used according to its approved land use category. Agricultural land cannot be used for residential or commercial purposes without permission.
Unauthorized land use may be declared illegal and attract penalties.
(UP Revenue Code, 2006 and Town Planning Laws)`
    },

    {
      question: "Why is Section 67 important for buyers?",
      answer: `Under Section 67 of the UP Revenue Code, the Tehsildar has the power to remove illegal occupation from government land.
This protects public land and warns buyers against unauthorized purchases.`
    },

    {
      question: "What are the risks of buying disputed property?",
      answer: `If a property is under court dispute, the buyer becomes bound by the final court decision.
This may result in financial loss or loss of possession.
(Civil Procedure Code, 1908 – Section 52, Doctrine of Lis Pendens)`
    },

    {
      question: "What are the rights of a property owner?",
      answer: `A property owner has the right to use, enjoy, transfer, lease, and inherit property.
However, these rights are subject to legal restrictions and regulatory compliance.
(UP Revenue Code, 2006 – Section 18)`
    },

    {
      question: "How does mutation happen after the death of the owner?",
      answer: `After the death of the property owner, legal heirs must apply for mutation by submitting the death certificate and succession documents.
Mutation updates revenue records but does not itself transfer ownership.
(UP Revenue Code, 2006 – Section 30)`
    },

    {
      question: "Which court handles property disputes?",
      answer: `Revenue courts handle land record and mutation issues.
Civil courts handle disputes related to ownership and possession.
(UP Revenue Code, 2006 – Section 116)`
    },

    {
      question: "Can property be bought through Power of Attorney?",
      answer: `No. The Supreme Court has clarified that Power of Attorney, Agreement to Sell, or Will do not transfer ownership.
Ownership transfers only through a Registered Sale Deed.
(Suraj Lamp Case – Supreme Court of India)`
    },

    {
      question: "Can agricultural land be sold as plots directly?",
      answer: `No. Agricultural land must be converted with proper land use permission before plotting.
(UP Revenue Code, 2006)`
    },

    {
      question: "Does previous owner's loan apply to the buyer?",
      answer: `Yes. If the property is subject to a mortgage or bank loan, liability remains attached to the property.
Buyers must verify loan clearance certificate or bank NOC before purchase.
(Transfer of Property Act, 1882 – Section 58)`
    },

    {
      question: "Can police help in possession disputes?",
      answer: `Police generally do not interfere in civil property disputes.
However, they may assist in executing valid court orders.
(Civil Procedure Code, 1908)`
    },

    {
      question: "Can houses on government land be regularized?",
      answer: `Regularization of houses built on government land depends on special government policies.
It is not a legal right.
(UP Revenue Code, 2006 – Section 67)`
    },

    {
      question: "Can lease rights be sold?",
      answer: `Lease rights may be transferred only as per lease conditions.
Unauthorized transfer is illegal.
(Transfer of Property Act, 1882 – Section 105)`
    },

    {
      question: "Can Income Tax Department take action on property?",
      answer: `Yes. The Income Tax Department may take action if undisclosed income or stamp duty evasion is detected.
(Income Tax Act)`
    },

    {
      question: "Can mistakes in property documents be corrected?",
      answer: `Yes. Errors may be corrected through a registered correction deed or through court intervention, depending on the nature of the mistake.
(Registration Rules)`
    }

  ]
},

/* ==========================================================
   SOCIAL & AGE (8 Cleaned)
========================================================== */
{
  category: "Social & Age Laws",
  questions: [

    {
      question: "Can a senior citizen file maintenance application even if they own property?",
      answer: `Yes. If the income or property owned is insufficient for basic needs, a senior citizen may seek maintenance under Section 4 of the Maintenance and Welfare of Parents and Senior Citizens Act, 2007.`
    },

    {
      question: "Can senior citizens reclaim property gifted to children?",
      answer: `Yes. Under Section 23 of the Maintenance and Welfare of Parents and Senior Citizens Act, 2007, property transferred subject to maintenance conditions can be declared void if care is not provided.`
    },

    {
      question: "Is a contract signed during mental incapacity valid?",
      answer: `No. For a contract to be valid under the Indian Contract Act, the party must be of sound mind at the time of signing.
Contracts signed during mental incapacity are generally unenforceable.`
    },

    {
      question: "What legal responsibility do children have towards parents?",
      answer: `Children (biological, adopted, or step) have a legal obligation to maintain their parents, including food, shelter, and medical care.`
    },

    {
      question: "Can a minor sign a binding contract?",
      answer: `No. Any agreement entered into by a minor (below 18 years) is void ab initio.
Such contracts have no legal effect and cannot be ratified after attaining majority.`
    },

    {
      question: "Does a child have a right over parent's self-acquired property?",
      answer: `No automatic right exists during the lifetime of the parent.
The parent has full discretion to transfer or dispose of self-acquired property.`
    }

  ]
},

/* ==========================================================
   RENTAL (15)
========================================================== */
{
  category: "Rental Law",
  questions: [

    {
      question: "What is a rental agreement?",
      answer: `A rental agreement is a legal contract between a landlord and tenant for use of property for a fixed period.
It defines rent amount, security deposit, duration, and rights and responsibilities of both parties.`
    },

    {
      question: "Is written rental agreement compulsory?",
      answer: `A written rental agreement is strongly recommended.
Long-term rentals may require registration. Oral agreements are difficult to prove legally.`
    },

    {
      question: "Can landlord increase rent anytime?",
      answer: `No. Rent increase must follow agreement terms and prior notice requirements.`
    },

    {
      question: "How much security deposit can landlord take?",
      answer: `Security deposit limits depend on state laws, generally ranging from two to six months' rent.`
    },

    {
      question: "Can landlord evict tenant without notice?",
      answer: `No. Eviction requires valid reason, written notice, and court order.`
    },

    {
      question: "Who pays maintenance and repairs?",
      answer: `Minor repairs are usually tenant’s responsibility.
Major structural repairs are landlord’s responsibility.`
    },

    {
      question: "Is subletting allowed?",
      answer: `Subletting is allowed only if the agreement permits it with landlord's written consent.`
    },

    {
      question: "Can landlord cut electricity or water?",
      answer: `No. Stopping essential services is illegal and may attract penalties.`
    }

  ]
},

/* ==========================================================
   CORPORATE (15)
========================================================== */
{
  category: "Corporate Law",
  questions: [

    {
      question: "What is a company?",
      answer: `A company is a separate legal entity registered under company law.
It can own property, sue, and be sued in its own name.`
    },

    {
      question: "What is Memorandum of Association (MOA)?",
      answer: `MOA defines the objectives and scope of activities of a company.`
    },

    {
      question: "What is Articles of Association (AOA)?",
      answer: `AOA contains internal rules governing company management.`
    },

    {
      question: "What is limited liability?",
      answer: `Shareholders are liable only up to the amount invested in the company.`
    },

    {
      question: "What is corporate governance?",
      answer: `Corporate governance ensures transparency, accountability, and ethical management of companies.`
    }

  ]
},

/* ==========================================================
   LABOUR (15)
========================================================== */
{
  category: "Labour Law",
  questions: [

    {
      question: "What is labour law?",
      answer: `Labour law regulates employer-employee relationships including wages, working hours, and workplace safety.`
    },

    {
      question: "What is minimum wage?",
      answer: `Minimum wage is the lowest legal salary payable to a worker. Paying less is illegal.`
    },

    {
      question: "What is gratuity?",
      answer: `Gratuity is a lump sum benefit paid to employees after long service, usually after five years of employment.`
    },

    {
      question: "What is maternity benefit?",
      answer: `Female employees are entitled to maternity leave with pay under law.`
    },

    {
      question: "What are penalties for labour law violations?",
      answer: `Employers violating labour laws may face fines, imprisonment, or cancellation of business licenses.`
    }

  ]
}

];
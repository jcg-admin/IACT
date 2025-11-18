export const MICROFRONTENDS_ANNOUNCEMENT = {
  title: 'Concept: Microfrontends',
  videoPlatforms: ['Youtube', 'Bilibili'],
  summary: [
    'A microfrontend is a microservice that exists within a browser.',
    'Microfrontends are sections of your UI, often consisting of dozens of components, that use frameworks like React, Vue, and Angular to render their components. Each microfrontend can be managed by a different team and may be implemented using its own framework. It is practical and suggested to use just one framework for all your microfrontends, although you may add additional frameworks when migrating or when experimenting.',
  ],
  sections: [
    {
      heading: 'Comparison to Microservices',
      paragraphs: [
        'Microservices are backend services that run in their own operating system process, control their own databases, and communicate with each other over the network.',
        'Compare that to microfrontends that all exist within a single browser tab: all browser JavaScript within a tab exists in a single operating system process (and even thread!). Browser JavaScript generally does not directly access databases, and communication within a browser tab happens in-memory instead of over the network.',
        "So what do they have in common??? Independent builds and deployments. Think of the DOM as the shared resource that your microfrontends are owning. One microfrontend's DOM should not be touched by another microfrontend, similar to how one backend microservice's database should not be touched by any microservice except the one that owns/controls it.",
      ],
    },
    {
      heading: 'Concrete Technical Definition',
      paragraphs: [
        'In the context of single-spa, a microfrontend is often an in-browser JavaScript module. You can read more about this in the recommended setup.',
      ],
    },
    {
      heading: 'Types of Microfrontends',
      paragraphs: ['In the context of single-spa, there are three kinds of microfrontends:'],
      list: [
        'single-spa applications: Microfrontends that render components for a set of specific routes.',
        'single-spa parcels: Microfrontends that render components without controlling routes.',
        'utility modules: Microfrontends that export shared JavaScript logic without rendering components.',
      ],
      closing:
        'A web app may include one or more types of microfrontends. See an in-depth comparison and our recommendations for choosing between microfrontend types.',
    },
    {
      heading: 'Communication between Microfrontends',
      paragraphs: [
        "import { thing } from 'other-microfrontend' is the preferred way to communicate between microfrontends. Here is some documentation that goes over this in more detail.",
      ],
      codeExample: "import { thing } from 'other-microfrontend'",
    },
    {
      heading: 'Relationship to single-spa',
      paragraphs: [
        'single-spa is a small, 5kb (gzipped) npm package that orchestrates the mounting and unmounting of your microfrontends. It knows when to mount the applications based on activity functions and can do so in a framework agnostic way with the help of small adapter libraries.',
      ],
    },
    {
      heading: 'Performance',
      paragraphs: [
        'Microfrontends are often more performant than the monoliths from which they originate. This is due to built-in lazy loading (via loading functions) and other performance-related best practices. Your monolith likely has "skeletons in its closet" - microfrontends gives you a migration path that will expose and resolve the problems caused by those skeletons.',
        'One important performance consideration is to share a single instance of large libraries (such as React, Vue, or Angular), which is highly encouraged. To do so, see our recommended setup.',
      ],
    },
  ],
  tasks: [
    'Mantener builds y despliegues independientes para cada microfrontend.',
    'Respetar los límites del DOM entre microfrontends tal como se hace con bases de datos en microservicios.',
    'Compartir una única instancia de librerías pesadas (React, Vue, Angular) siempre que sea posible.',
  ],
};

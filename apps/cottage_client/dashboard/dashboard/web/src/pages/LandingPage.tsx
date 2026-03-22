import { useState } from 'react';
import {
  ArrowRight,
  CheckCircle2,
  Cpu,
  Eye,
  Radio,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { SalesFunnel } from '../components/sales/SalesFunnel';
import { Header } from '../components/layout/Header';
import { Footer } from '../components/layout/Footer';
import '../styles/LandingPage.css';

const robotProfiles = [
  {
    id: 'r1',
    eyebrow: 'Humanoid platform',
    name: 'R1 Humanoid',
    image: '/images/robots/go2-hero.png',
    summary: 'Front-of-house presence, inspection, guided handling, and workflows that need a human-shaped interface.',
    stats: ['26 DOF', '1.22m reach profile', 'Voice + vision ready'],
    strengths: ['Reception and guided tours', 'Inspection and exception handling', 'Custom AI copilots for staff workflows'],
  },
  {
    id: 'go2',
    eyebrow: 'Quadruped platform',
    name: 'Go2 Robot Dog',
    image: '/images/robots/r1-hero.png',
    summary: 'Mobile patrol, mapping, and coverage for facilities that need terrain tolerance and persistent roaming.',
    stats: ['4D LiDAR', '2.5m/s top speed', 'All-terrain mobility'],
    strengths: ['Security and perimeter patrols', 'Warehouse rounds and digital twins', 'Remote inspection in constrained spaces'],
  },
];

const operatingModel = [
  {
    icon: Radio,
    title: 'Live fleet telemetry',
    text: 'See what every robot is doing, where it is, and which exceptions need a human decision.',
  },
  {
    icon: Cpu,
    title: 'Mission-level automation',
    text: 'Move beyond joystick demos into repeatable inspection, delivery, sanitation, and client-specific runbooks.',
  },
  {
    icon: Eye,
    title: 'Vision and AI assistance',
    text: 'Layer perception, detection, and operator guidance onto deployments instead of bolting it on later.',
  },
  {
    icon: ShieldCheck,
    title: 'Operator controls',
    text: 'Provision fleets, onboard robots, and keep a human in the loop for deployment safety and support.',
  },
];

const deploymentSteps = [
  {
    step: '01',
    title: 'Plan the workflow',
    text: 'Select the robot type, facility constraints, operator handoffs, and the KPI that must move first.',
  },
  {
    step: '02',
    title: 'Simulate and prove',
    text: 'Validate routes, tasks, and failure handling in simulation before pushing commands to hardware.',
  },
  {
    step: '03',
    title: 'Launch the fleet',
    text: 'Provision robots, assign them to sites, and track status from a single commercial and operations surface.',
  },
];

const pricingTiers = [
  {
    name: 'Pilot',
    tag: 'Best for first deployment',
    price: 'From $5.9k',
    details: 'Single-site pilot with onboarding, mission design, and an operator-ready dashboard.',
    points: ['1-2 robots', 'Onboarding workflow', 'Scenario-based simulation', 'Demo-to-pilot handoff'],
  },
  {
    name: 'Operations',
    tag: 'For active fleets',
    price: 'Custom program',
    details: 'Fleet segmentation, provisioning, telemetry, and remote operations for multi-robot environments.',
    points: ['Fleet and robot management', 'Client-facing reporting', 'Remote operations center', 'Use-case customization'],
  },
  {
    name: 'Enterprise',
    tag: 'For multi-site rollouts',
    price: 'Strategic pricing',
    details: 'Commercial rollout support for organizations standardizing robotics across sites and business units.',
    points: ['Multi-site templates', 'Dedicated rollout design', 'Custom integrations', 'Executive ROI reporting'],
  },
];

const useCases = [
  'Warehouse audit and restock support',
  'Facility security and after-hours patrol',
  'Client-facing tours, check-in, and reception',
  'Sanitation, rounds, and exception escalation',
];

const taskSeries = [
  {
    title: 'Bathroom cleaning',
    eyebrow: 'Task image series',
    image: '/images/robots/g1-bathroom.png',
    fallbackImage: '/images/robots/go2-hero.png',
    description:
      'Show the humanoid in a concrete, understandable workflow. Bathroom cleaning is a strong first image because it makes the labor use case immediate.',
    points: [
      'Turns the robot from concept into a visible job',
      'Makes sanitation and service use cases easier to sell',
      'Builds a repeatable gallery for future task imagery',
    ],
  },
  {
    title: 'Retail shelf restocking',
    eyebrow: 'Task image series',
    image: '/images/robots/g1-grocery.png',
    fallbackImage: '/images/robots/go2-hero.png',
    description:
      'Show the humanoid working directly in a retail aisle. Restocking makes the labor story concrete for stores, grocers, and multi-site operators.',
    points: [
      'Demonstrates shelf-facing retail execution',
      'Extends the story from service into inventory work',
      'Helps buyers imagine repeatable in-store deployment',
    ],
  },
];

export function LandingPage() {
  const [showSalesFunnel, setShowSalesFunnel] = useState(false);

  if (showSalesFunnel) {
    return (
      <SalesFunnel
        onComplete={(lead) => {
          console.log('Lead completed:', lead);
          setShowSalesFunnel(false);
        }}
      />
    );
  }

  return (
    <div className="landing-page">
      <Header />

      <main className="landing-main">
        <section className="hero-section" id="top">
          <div className="hero-copy">
            <div className="hero-badge">
              <Sparkles size={16} />
              <span>Humanoid-led robot fleets for deployment, onboarding, and operations</span>
            </div>

            <p className="hero-kicker">Commercial robotics, built for rollout.</p>
            <h1 className="hero-title">Robot Fleets for Real Business.</h1>
            <p className="hero-subtitle">
              Deploy humanoid-led fleets with the commercial, onboarding, simulation, and operations layer needed to
              move from pilot to production.
            </p>

            <div className="hero-cta">
              <button className="btn-primary" onClick={() => setShowSalesFunnel(true)}>
                Launch Sales Funnel
                <ArrowRight size={18} />
              </button>
              <a className="btn-secondary" href="#pricing">
                View Packages
              </a>
            </div>

            <div className="hero-proof">
              <div className="proof-card">
                <span className="proof-value">40%</span>
                <span className="proof-label">Targeted cost reduction</span>
              </div>
              <div className="proof-card">
                <span className="proof-value">3x</span>
                <span className="proof-label">Expected productivity lift</span>
              </div>
              <div className="proof-card">
                <span className="proof-value">60 days</span>
                <span className="proof-label">Pilot timeline from plan to site</span>
              </div>
            </div>
          </div>

          <div className="hero-panel">
            <div className="hero-visual">
              <div className="hero-visual-frame">
                <img
                  src="/images/robots/g1-fleet.png"
                  alt="Humanoid robot fleet"
                  className="hero-visual-image"
                  loading="eager"
                />
              </div>
            </div>

            <div className="hero-visual-caption">
              <span className="hero-visual-caption-badge">Fleet-ready deployment</span>
              <p>Humanoid fleets configured for repeatable labor coverage across sanitation, retail, inspection, and daily operations.</p>
            </div>
          </div>
        </section>

        <section className="trust-strip" aria-label="Key value statements">
          <div className="trust-item">Lower labor costs with repeatable robot assignments</div>
          <div className="trust-item">Move from buyer interest to onboarded fleet without hand-built process</div>
          <div className="trust-item">Designed for operators, not just robotics demos</div>
        </section>

        <section className="task-series-section">
          <div className="section-heading">
            <p className="section-kicker">Task image series</p>
            <h2>Lower labor costs with robots assigned to real operational work.</h2>
            <p>
              Frame each deployment around a measurable task. Start with sanitation and restocking, then expand into
              reception, inspection, and patrol as the fleet takes on more daily work.
            </p>
          </div>

          <div className="task-series-grid">
            {taskSeries.map((task) => (
              <article className="task-spotlight-card" key={task.title}>
                <div className="task-spotlight-media">
                  <img
                    src={task.image}
                    alt={`Humanoid robot performing ${task.title}`}
                    loading="eager"
                    onError={(event) => {
                      const target = event.currentTarget;
                      target.onerror = null;
                      target.src = task.fallbackImage;
                    }}
                  />
                </div>

                <div className="task-spotlight-copy">
                  <span className="task-spotlight-eyebrow">{task.eyebrow}</span>
                  <h3>{task.title}</h3>
                  <p>{task.description}</p>

                  <ul className="task-spotlight-points">
                    {task.points.map((point) => (
                      <li key={point}>
                        <CheckCircle2 size={16} />
                        <span>{point}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="robots-section" id="robots">
          <div className="section-heading">
            <p className="section-kicker">Robot lineup</p>
            <h2>Two robot profiles, one commercial story.</h2>
            <p>
              Lead with the right platform for the workflow, then move the buyer into a deployment model that already
              reflects onboarding and fleet operations.
            </p>
          </div>

          <div className="robot-grid">
            {robotProfiles.map((robot, index) => (
              <article className={`robot-card ${index === 0 ? 'robot-card-featured' : 'robot-card-secondary'}`} id={robot.id} key={robot.id}>
                <div className="robot-image-shell">
                  <img src={robot.image} alt={robot.name} className="robot-image" loading="eager" />
                  <span className="robot-eyebrow">{robot.eyebrow}</span>
                </div>

                <div className="robot-content">
                  <h3>{robot.name}</h3>
                  <p className="robot-summary">{robot.summary}</p>

                  <div className="robot-stat-row">
                    {robot.stats.map((stat) => (
                      <span className="robot-pill" key={stat}>
                        {stat}
                      </span>
                    ))}
                  </div>

                  <ul className="robot-strengths">
                    {robot.strengths.map((strength) => (
                      <li key={strength}>
                        <CheckCircle2 size={16} />
                        <span>{strength}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="platform-section" id="features">
          <div className="section-heading">
            <p className="section-kicker">Platform value</p>
            <h2>One layer for deployment, control, and scale.</h2>
            <p>
              Qualify the use case, simulate the workflow, onboard the fleet, and keep operations visible after the
              robots are live in the field.
            </p>
          </div>

          <div className="platform-grid">
            {operatingModel.map(({ icon: Icon, title, text }) => (
              <article className="platform-card" key={title}>
                <div className="platform-icon">
                  <Icon size={20} />
                </div>
                <h3>{title}</h3>
                <p>{text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="showcase-section">
          <div className="showcase-copy">
            <p className="section-kicker">Where fleets work</p>
            <h2>Use cases that justify a real deployment.</h2>
            <p>
              Start with labor-intensive workflows that buyers already budget for, then expand coverage as the fleet
              proves reliability and cost savings.
            </p>

            <div className="use-case-list">
              {useCases.map((useCase) => (
                <div className="use-case-item" key={useCase}>
                  <CheckCircle2 size={16} />
                  <span>{useCase}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="showcase-visual">
            <div className="showcase-stack">
              <img src="/images/robots/r1-action.jpg" alt="R1 in a commercial deployment context" />
              <img src="/images/robots/go2-action.jpg" alt="Go2 in a mobile field context" />
            </div>
          </div>
        </section>

        <section className="timeline-section">
          <div className="section-heading">
            <p className="section-kicker">Rollout path</p>
            <h2>A clearer progression from interest to deployed fleet.</h2>
          </div>

          <div className="timeline-grid">
            {deploymentSteps.map((step) => (
              <article className="timeline-card" key={step.step}>
                <span className="timeline-step">{step.step}</span>
                <h3>{step.title}</h3>
                <p>{step.text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="pricing-section" id="pricing">
          <div className="section-heading">
            <p className="section-kicker">Commercial packaging</p>
            <h2>Pricing that matches how robotics programs actually get approved.</h2>
            <p>
              Start with a pilot, prove labor value, then expand into operating plans and broader fleet rollouts.
            </p>
          </div>

          <div className="pricing-grid">
            {pricingTiers.map((tier) => (
              <article className="pricing-card" key={tier.name}>
                <div className="pricing-header">
                  <span className="pricing-tag">{tier.tag}</span>
                  <h3>{tier.name}</h3>
                  <div className="pricing-price">{tier.price}</div>
                  <p>{tier.details}</p>
                </div>

                <ul className="pricing-points">
                  {tier.points.map((point) => (
                    <li key={point}>
                      <CheckCircle2 size={16} />
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </section>

        <section className="cta-section" id="contact">
          <div className="cta-panel">
            <div>
              <p className="section-kicker">Next step</p>
              <h2>Turn this into a real sales conversation.</h2>
              <p>
                Move directly into the sales funnel, capture the buyer context, and align the robot choice with the
                deployment plan.
              </p>
            </div>

            <div className="cta-actions">
              <button className="btn-primary" onClick={() => setShowSalesFunnel(true)}>
                Start Qualification
                <ArrowRight size={18} />
              </button>
              <a className="btn-secondary" href="#top">
                Back to top
              </a>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}

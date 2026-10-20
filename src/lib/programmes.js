import programmes from '../data/programmes.json';
import projects from '../data/projects.json';

const bySlug = Object.fromEntries(projects.map((p) => [p.slug, p]));

// Count tools or skills across a programme's projects, merging case variants.
function tally(list, key) {
  const m = new Map();
  for (const p of list) for (const raw of p[key] || []) {
    const k = raw.trim().toLowerCase();
    if (!k) continue;
    const e = m.get(k) || { name: raw.trim(), n: 0 };
    e.n += 1; m.set(k, e);
  }
  return [...m.values()].sort((a, b) => b.n - a.n || a.name.localeCompare(b.name));
}

export const programmeList = programmes.map((g) => {
  const lead = g.lead ? bySlug[g.lead] : null;
  const members = g.members.map((s) => bySlug[s]).filter(Boolean);
  const all = lead ? [lead, ...members] : members;
  return { ...g, leadProject: lead, memberProjects: members, all, tools: tally(all, 'methods'), skills: tally(all, 'skills') };
});

export const programmeOf = Object.fromEntries(programmeList.flatMap((g) => g.all.map((p) => [p.slug, g])));

// Old /projects/#area-… links land on the closest programme.
export const areaToProgramme = { biomedical: 'microbes', 'public-health': 'epidemics', science: 'africa-equity', patents: 'phage', data: 'preprints', ai: 'innovation' };

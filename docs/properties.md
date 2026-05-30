# Materials Properties

This document lists the materials properties that **n-Op** — the neural
operator model developed in this repository — is designed to simulate.
The categories below define the target scope: any quantity a user might
ask the model to predict should fall into one of them.

### 1. Structural properties

The geometric description of a material — the spatial arrangement of atoms
and the resulting unit cell, surfaces, and imperfections. Every other
property in this list is built on top of an accurate structure, so errors
here propagate everywhere downstream.

- Lattice parameters
- Bond lengths
- Crystal structure
- Defects
- Surfaces

### 2. Electronic properties

How electrons populate the available energy levels and distribute
themselves through the crystal. These quantities decide whether a material
is a metal, semiconductor, or insulator, and they feed almost every other
category — optical, magnetic, transport, and chemical behavior all
ultimately trace back here.

- Band structure
- Density of states
- Band gap
- Charge density

### 3. Optical properties

How the material responds to light: which photon energies it absorbs,
how its refractive index changes with frequency, and how excited electrons
release energy when they relax. These properties govern color, transparency,
and any photonic or optoelectronic application.

- Absorption
- Dielectric function
- Refractive index
- Photoluminescence trends

### 4. Mechanical properties

How the material deforms and resists deformation under applied force.
These tensors and scalar quantities describe stiffness, compressibility,
and the yielding and hardness behavior that determine whether a material
can survive a given mechanical environment.

- Elastic constants
- Bulk modulus
- Stress–strain response
- Hardness trends

### 5. Thermal properties

How vibrational modes (phonons) of the lattice store and transport heat.
These properties set the heat capacity, the rate at which a material
conducts thermal energy, and how it expands with temperature — all
critical for thermoelectric, thermal-management, and high-temperature
applications.

- Phonons
- Heat capacity
- Thermal conductivity
- Thermal expansion

### 6. Magnetic properties

The configuration and interaction of electron spins. These quantities
determine whether a material is ferromagnetic, antiferromagnetic, or
paramagnetic, and they control phenomena from data storage to
spintronics.

- Magnetic moment
- Spin density
- Exchange interactions

### 7. Transport / diffusion properties

How charge carriers and ions move through the material under external
fields or concentration gradients. These properties govern electrical
conductivity, ionic conduction in batteries and fuel cells, and the
activation energies for atomic migration.

- Carrier mobility
- Ionic diffusion
- Conductivity
- Migration barriers

### 8. Thermodynamic properties

The energetic landscape that decides which phases of matter are stable,
which are metastable, and which will spontaneously transform. Total
and formation energies, along with free energies, drive phase-diagram
construction and any prediction of synthesizability.

- Total energy
- Formation energy
- Phase stability
- Free energy

### 9. Chemical / surface properties

How atoms and molecules bind to a material's surface and how they
rearrange along reaction pathways. These properties underlie catalysis,
corrosion, and almost every interfacial process where the material
interacts chemically with its environment.

- Adsorption energy
- Reaction pathways
- Catalytic activity
- Surface energy

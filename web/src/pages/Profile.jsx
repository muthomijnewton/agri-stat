import { useState, useEffect } from 'react'
import { authAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'
import '../css/pages.css'
import '../css/profile.css'

/* ---- Icons ---- */
function IconUser() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
    </svg>
  )
}
function IconBuilding() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="2" y="7" width="20" height="14" rx="2" /><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
    </svg>
  )
}
function IconMapPin() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z" /><circle cx="12" cy="10" r="3" />
    </svg>
  )
}
function IconLeaf() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z" />
      <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
    </svg>
  )
}
function IconLock() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  )
}
function IconCheck() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ width: 14, height: 14 }}>
      <polyline points="20 6 9 17 4 12" />
    </svg>
  )
}

/* ---- Section wrapper ---- */
function ProfileSection({ icon, title, children }) {
  return (
    <section className="profile-section card">
      <h2 className="profile-section-title">
        <span className="profile-section-icon">{icon}</span>
        {title}
      </h2>
      {children}
    </section>
  )
}

/* ---- Avatar initials ---- */
function Avatar({ name, username }) {
  const initials = name
    ? name.split(' ').map((w) => w[0]).slice(0, 2).join('').toUpperCase()
    : (username ?? '?')[0].toUpperCase()
  return <div className="profile-avatar" aria-hidden="true">{initials}</div>
}

export default function Profile() {
  const { user, updateUser } = useAuth()

  const [profile,    setProfile]    = useState(null)
  const [loading,    setLoading]    = useState(true)
  const [saving,     setSaving]     = useState(false)
  const [error,      setError]      = useState(null)
  const [successMsg, setSuccessMsg] = useState(null)

  // Controlled form state — one flat object for all editable fields
  const [form, setForm] = useState(null)

  // Password change fields kept separate so they never accidentally serialize
  const [pwForm, setPwForm] = useState({ current_password: '', new_password: '', confirm_password: '' })
  const [pwError,   setPwError]   = useState(null)
  const [pwSuccess, setPwSuccess] = useState(null)
  const [savingPw,  setSavingPw]  = useState(false)

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await authAPI.getProfile()
        setProfile(data)
        setForm({
          full_name:         data.full_name         ?? '',
          email:             data.email             ?? '',
          phone:             data.phone             ?? '',
          business_name:     data.business_name     ?? '',
          business_type:     data.business_type     ?? '',
          country:           data.country           ?? '',
          county:            data.county            ?? '',
          sub_county:        data.sub_county        ?? '',
          village:           data.village           ?? '',
          farm_size:         data.farm_size         ?? '',
          primary_crop:      data.primary_crop      ?? '',
          primary_livestock: data.primary_livestock ?? '',
          currency:          data.currency          ?? 'KES',
          bio:               data.bio               ?? '',
        })
      } catch (err) {
        setError(err.response?.data?.detail ?? err.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSave = async (e) => {
    e.preventDefault()
    try {
      setSaving(true)
      setError(null)
      const { data } = await authAPI.updateProfile(form)
      setProfile(data)
      updateUser(data)
      flash('Profile saved successfully.')
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    } finally {
      setSaving(false)
    }
  }

  const handlePasswordChange = async (e) => {
    e.preventDefault()
    setPwError(null)
    if (pwForm.new_password !== pwForm.confirm_password) {
      setPwError('New passwords do not match.')
      return
    }
    if (pwForm.new_password.length < 6) {
      setPwError('New password must be at least 6 characters.')
      return
    }
    try {
      setSavingPw(true)
      await authAPI.updateProfile({
        current_password: pwForm.current_password,
        new_password:     pwForm.new_password,
      })
      setPwForm({ current_password: '', new_password: '', confirm_password: '' })
      setPwSuccess('Password changed successfully.')
      setTimeout(() => setPwSuccess(null), 4000)
    } catch (err) {
      setPwError(err.response?.data?.detail ?? err.message)
    } finally {
      setSavingPw(false)
    }
  }

  const flash = (msg) => {
    setSuccessMsg(msg)
    setTimeout(() => setSuccessMsg(null), 3500)
  }

  if (loading) return <div className="loading">Loading profile…</div>
  if (!form)   return <div className="error">{error ?? 'Failed to load profile.'}</div>

  return (
    <div className="container">
      <div className="page-header">
        <h1>Profile</h1>
      </div>

      {error      && <div className="error">{error}</div>}
      {successMsg && <div className="success">{successMsg}</div>}

      {/* ── Profile header card ── */}
      <div className="profile-header card">
        <Avatar name={profile.full_name} username={profile.username} />
        <div className="profile-header-info">
          <h2>{profile.full_name || profile.username}</h2>
          <p className="text-muted">{profile.email}</p>
          <div className="profile-header-meta">
            {profile.business_name && <span>{profile.business_name}</span>}
            {profile.county        && <span>{profile.county}, {profile.country || 'Kenya'}</span>}
            {profile.primary_crop  && <span>Crops: {profile.primary_crop}</span>}
            <span className={`badge ${profile.is_admin ? 'badge-info' : 'badge-secondary'}`}>
              {profile.is_admin ? 'Administrator' : 'Farmer'}
            </span>
          </div>
        </div>
        <div className="profile-header-since">
          <p className="text-muted" style={{ fontSize: '0.8rem' }}>Member since</p>
          <p style={{ fontWeight: 600, fontSize: '0.875rem' }}>
            {new Date(profile.created_at).toLocaleDateString('en-KE', { year: 'numeric', month: 'long' })}
          </p>
        </div>
      </div>

      <form onSubmit={handleSave}>
        {/* ── Personal information ── */}
        <ProfileSection icon={<IconUser />} title="Personal Information">
          <div className="form-row">
            <div className="form-group">
              <label>Full Name</label>
              <input type="text" name="full_name" value={form.full_name} onChange={handleChange} placeholder="Your full name" />
            </div>
            <div className="form-group">
              <label>Email Address</label>
              <input type="email" name="email" value={form.email} onChange={handleChange} required />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Phone Number</label>
              <input type="tel" name="phone" value={form.phone} onChange={handleChange} placeholder="+254 7xx xxx xxx" />
            </div>
            <div className="form-group">
              <label>Preferred Currency</label>
              <select name="currency" value={form.currency} onChange={handleChange}>
                <option value="KES">KES — Kenyan Shilling</option>
                <option value="USD">USD — US Dollar</option>
                <option value="UGX">UGX — Ugandan Shilling</option>
                <option value="TZS">TZS — Tanzanian Shilling</option>
                <option value="ETB">ETB — Ethiopian Birr</option>
                <option value="RWF">RWF — Rwandan Franc</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Bio</label>
            <textarea name="bio" value={form.bio} onChange={handleChange} rows="3" placeholder="Tell us about yourself and your farming operation…" />
          </div>
        </ProfileSection>

        {/* ── Business information ── */}
        <ProfileSection icon={<IconBuilding />} title="Business Information">
          <div className="form-row">
            <div className="form-group">
              <label>Business / Farm Name</label>
              <input type="text" name="business_name" value={form.business_name} onChange={handleChange} placeholder="e.g., Mwangi Family Farm" />
            </div>
            <div className="form-group">
              <label>Business Type</label>
              <select name="business_type" value={form.business_type} onChange={handleChange}>
                <option value="Farmer">Farmer</option>
                <option value="Cooperative">Cooperative</option>
                <option value="Trader">Trader / Middleman</option>
                <option value="Processor">Food Processor</option>
                <option value="Exporter">Exporter</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>
        </ProfileSection>

        {/* ── Location ── */}
        <ProfileSection icon={<IconMapPin />} title="Location">
          <div className="form-row">
            <div className="form-group">
              <label>Country</label>
              <select name="country" value={form.country} onChange={handleChange}>
                <option value="Kenya">Kenya</option>
                <option value="Uganda">Uganda</option>
                <option value="Tanzania">Tanzania</option>
                <option value="Rwanda">Rwanda</option>
                <option value="Ethiopia">Ethiopia</option>
                <option value="South Sudan">South Sudan</option>
                <option value="Burundi">Burundi</option>
              </select>
            </div>
            <div className="form-group">
              <label>County / Region</label>
              <input type="text" name="county" value={form.county} onChange={handleChange} placeholder="e.g., Uasin Gishu" />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Sub-County / District</label>
              <input type="text" name="sub_county" value={form.sub_county} onChange={handleChange} placeholder="e.g., Turbo" />
            </div>
            <div className="form-group">
              <label>Village / Ward</label>
              <input type="text" name="village" value={form.village} onChange={handleChange} placeholder="e.g., Soy" />
            </div>
          </div>
        </ProfileSection>

        {/* ── Farm information ── */}
        <ProfileSection icon={<IconLeaf />} title="Farm Information">
          <div className="form-row">
            <div className="form-group">
              <label>Farm Size</label>
              <input type="text" name="farm_size" value={form.farm_size} onChange={handleChange} placeholder="e.g., 5 acres, 2 ha" />
            </div>
            <div className="form-group">
              <label>Primary Crop</label>
              <input type="text" name="primary_crop" value={form.primary_crop} onChange={handleChange} placeholder="e.g., Maize, Tomatoes" />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Primary Livestock</label>
              <input type="text" name="primary_livestock" value={form.primary_livestock} onChange={handleChange} placeholder="e.g., Dairy cattle, Poultry" />
            </div>
          </div>
        </ProfileSection>

        <div className="profile-save-row">
          <button type="submit" className="btn-primary" disabled={saving}>
            <IconCheck /> {saving ? 'Saving…' : 'Save Profile'}
          </button>
        </div>
      </form>

      {/* ── Password change — separate form so it doesn't submit with the profile ── */}
      <ProfileSection icon={<IconLock />} title="Change Password">
        {pwError   && <div className="error"  style={{ marginBottom: '1rem' }}>{pwError}</div>}
        {pwSuccess && <div className="success" style={{ marginBottom: '1rem' }}>{pwSuccess}</div>}
        <form onSubmit={handlePasswordChange}>
          <div className="form-row">
            <div className="form-group">
              <label>Current Password *</label>
              <input
                type="password"
                value={pwForm.current_password}
                onChange={(e) => setPwForm((p) => ({ ...p, current_password: e.target.value }))}
                required
                autoComplete="current-password"
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>New Password *</label>
              <input
                type="password"
                value={pwForm.new_password}
                onChange={(e) => setPwForm((p) => ({ ...p, new_password: e.target.value }))}
                required
                autoComplete="new-password"
                placeholder="Min. 6 characters"
              />
            </div>
            <div className="form-group">
              <label>Confirm New Password *</label>
              <input
                type="password"
                value={pwForm.confirm_password}
                onChange={(e) => setPwForm((p) => ({ ...p, confirm_password: e.target.value }))}
                required
                autoComplete="new-password"
              />
            </div>
          </div>
          <button type="submit" className="btn-primary" disabled={savingPw}>
            <IconLock /> {savingPw ? 'Changing…' : 'Change Password'}
          </button>
        </form>
      </ProfileSection>
    </div>
  )
}
